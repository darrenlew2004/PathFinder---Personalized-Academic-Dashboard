from cassandra.cluster import Cluster, Session, EXEC_PROFILE_DEFAULT, ExecutionProfile
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.io.geventreactor import GeventConnection
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class CassandraService:
    _instance: Optional['CassandraService'] = None
    _session: Optional[Session] = None
    _cluster: Optional[Cluster] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._session is None:
            self._connect()
    
    def _connect(self):
        """Establish connection to Cassandra"""
        logger.info(f"Connecting to Cassandra at {settings.CASSANDRA_HOST}:{settings.CASSANDRA_PORT}")
        
        try:
            # Configure authentication if credentials provided
            auth_provider = None
            if settings.CASSANDRA_USERNAME and settings.CASSANDRA_PASSWORD:
                logger.info("Using authentication for Cassandra connection")
                auth_provider = PlainTextAuthProvider(
                    username=settings.CASSANDRA_USERNAME,
                    password=settings.CASSANDRA_PASSWORD
                )
            else:
                logger.info("No authentication configured for Cassandra")
            
            # Create execution profile with load balancing policy
            profile = ExecutionProfile(
                load_balancing_policy=DCAwareRoundRobinPolicy(local_dc=settings.CASSANDRA_DATACENTER),
                request_timeout=10
            )
            
            # Create cluster connection with gevent event loop (Python 3.12+ compatible)
            self._cluster = Cluster(
                contact_points=[settings.CASSANDRA_HOST],
                port=settings.CASSANDRA_PORT,
                auth_provider=auth_provider,
                protocol_version=4,
                connect_timeout=10,
                control_connection_timeout=10,
                execution_profiles={EXEC_PROFILE_DEFAULT: profile},
                connection_class=GeventConnection
            )
            
            # Connect and get session
            self._session = self._cluster.connect()
            
            # Use the existing keyspace (assume it already exists)
            logger.info(f"Connecting to keyspace: {settings.CASSANDRA_KEYSPACE}")
            self._session.set_keyspace(settings.CASSANDRA_KEYSPACE)
            
            # Create tables if they don't exist (if user has permissions)
            try:
                self._create_tables()
            except Exception as e:
                logger.warning(f"Could not create tables (may already exist or lack permissions): {str(e)}")
            
            logger.info("Successfully connected to Cassandra")
            
        except Exception as e:
            logger.error(f"Failed to connect to Cassandra: {str(e)}")
            # Don't re-raise here so the application can start even if Cassandra is
            # unavailable (useful for local development or when Cassandra is down).
            # Leave _session/_cluster as None and allow callers to handle missing
            # connection when they attempt to use the database.
            self._session = None
            self._cluster = None
    
    def _create_keyspace(self):
        """Create keyspace if it doesn't exist"""
        query = f"""
            CREATE KEYSPACE IF NOT EXISTS {settings.CASSANDRA_KEYSPACE}
            WITH replication = {{
                'class': 'SimpleStrategy',
                'replication_factor': 1
            }}
        """
        self._session.execute(query)
        logger.info(f"Keyspace {settings.CASSANDRA_KEYSPACE} created or already exists")
    
    def _create_tables(self):
        """Create all required tables"""
        keyspace = settings.CASSANDRA_KEYSPACE
        
        # Students table
        self._session.execute(f"""
            CREATE TABLE IF NOT EXISTS {keyspace}.students (
                id UUID PRIMARY KEY,
                student_id TEXT,
                name TEXT,
                email TEXT,
                password_hash TEXT,
                gpa DOUBLE,
                semester INT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # Courses table
        self._session.execute(f"""
            CREATE TABLE IF NOT EXISTS {keyspace}.courses (
                id UUID PRIMARY KEY,
                course_code TEXT,
                course_name TEXT,
                credits INT,
                difficulty DOUBLE,
                prerequisites LIST<TEXT>,
                description TEXT,
                created_at TIMESTAMP
            )
        """)
        
        # Enrollments table
        self._session.execute(f"""
            CREATE TABLE IF NOT EXISTS {keyspace}.enrollments (
                id UUID PRIMARY KEY,
                student_id UUID,
                course_id UUID,
                semester INT,
                grade TEXT,
                status TEXT,
                attendance_rate DOUBLE,
                enrolled_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        # Risk predictions table
        self._session.execute(f"""
            CREATE TABLE IF NOT EXISTS {keyspace}.risk_predictions (
                id UUID PRIMARY KEY,
                student_id UUID,
                course_id UUID,
                risk_level TEXT,
                confidence DOUBLE,
                factors MAP<TEXT, DOUBLE>,
                recommendations LIST<TEXT>,
                predicted_grade TEXT,
                created_at TIMESTAMP
            )
        """)
        
        logger.info("All tables created or already exist")
    
    def get_session(self) -> Session:
        """Get the Cassandra session"""
        if self._session is None:
            self._connect()
        return self._session
    
    def execute(self, query: str, parameters: tuple = None):
        """Execute a query synchronously"""
        session = self.get_session()
        if parameters:
            return session.execute(query, parameters)
        return session.execute(query)
    
    def execute_async(self, query: str, parameters: tuple = None):
        """Execute a query asynchronously"""
        session = self.get_session()
        if parameters:
            return session.execute_async(query, parameters)
        return session.execute_async(query)
    
    def close(self):
        """Close the Cassandra connection"""
        if self._cluster:
            self._cluster.shutdown()
            logger.info("Cassandra connection closed")


# Singleton instance
cassandra_service = CassandraService()
