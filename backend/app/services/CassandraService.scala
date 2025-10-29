package services

import com.datastax.oss.driver.api.core.{CqlSession, CqlSessionBuilder}
import com.datastax.oss.driver.api.core.config.{DriverConfigLoader, DefaultDriverOption}
import com.datastax.oss.driver.api.core.cql.{AsyncResultSet, ResultSet, Row}
import javax.inject._
import play.api.{Configuration, Logger}
import scala.concurrent.{ExecutionContext, Future, Promise}
import scala.jdk.CollectionConverters._
import scala.util.{Try, Success, Failure}
import java.net.InetSocketAddress
import com.datastax.oss.driver.api.core.`type`.DataTypes
import com.datastax.oss.driver.api.querybuilder.SchemaBuilder

@Singleton
class CassandraService @Inject()(
  config: Configuration
)(implicit ec: ExecutionContext) {
  
  private val logger = Logger(this.getClass)
  
  private val contactPoint: String = config.get[String]("cassandra.contactPoint")
  private val port: Int = config.get[Int]("cassandra.port")
  private val keyspace: String = config.get[String]("cassandra.keyspace")
  private val datacenter: String = config.getOptional[String]("cassandra.datacenter").getOrElse("datacenter1")
  
  private var sessionOpt: Option[CqlSession] = None
  
  def getSession: CqlSession = {
    sessionOpt.getOrElse {
      val newSession = createSession()
      sessionOpt = Some(newSession)
      newSession
    }
  }
  
  private def createSession(): CqlSession = {
    logger.info(s"Connecting to Cassandra at $contactPoint:$port, keyspace: $keyspace")
    
    try {
      val configLoader = DriverConfigLoader.programmaticBuilder()
        .withString(DefaultDriverOption.REQUEST_TIMEOUT, "10 seconds")
        .withString(DefaultDriverOption.CONNECTION_CONNECT_TIMEOUT, "10 seconds")
        .withString(DefaultDriverOption.CONNECTION_INIT_QUERY_TIMEOUT, "10 seconds")
        .build()
      
      // Optional auth from config
      val usernameOpt = config.getOptional[String]("cassandra.username")
      val passwordOpt = config.getOptional[String]("cassandra.password")

      var builder = CqlSession.builder()
        .addContactPoint(new InetSocketAddress(contactPoint, port))
        .withLocalDatacenter(datacenter)
        .withConfigLoader(configLoader)

      (usernameOpt, passwordOpt) match {
        case (Some(u), Some(p)) =>
          logger.info("Cassandra auth credentials provided in config — enabling authentication")
          builder = builder.withAuthCredentials(u, p)
        case _ =>
          logger.info("No Cassandra auth credentials found in config — attempting unauthenticated connection")
      }

      val session = builder.build()
      
      // Create keyspace if it doesn't exist
      createKeyspaceIfNotExists(session)
      
      // Switch to keyspace
      session.execute(s"USE $keyspace")
      
      // Create tables
      createTables(session)
      
      logger.info("Successfully connected to Cassandra")
      session
    } catch {
      case e: Exception =>
        logger.error(s"Failed to connect to Cassandra: ${e.getMessage}", e)
        throw e
    }
  }
  
  private def createKeyspaceIfNotExists(session: CqlSession): Unit = {
    val createKeyspace = s"""
      CREATE KEYSPACE IF NOT EXISTS $keyspace
      WITH replication = {
        'class': 'SimpleStrategy',
        'replication_factor': 1
      }
    """
    session.execute(createKeyspace)
    logger.info(s"Keyspace $keyspace created or already exists")
  }
  
  private def createTables(session: CqlSession): Unit = {
    // Students table
    session.execute(s"""
      CREATE TABLE IF NOT EXISTS $keyspace.students (
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
    
    session.execute(s"""
      CREATE INDEX IF NOT EXISTS students_email_idx 
      ON $keyspace.students (email)
    """)
    
    session.execute(s"""
      CREATE INDEX IF NOT EXISTS students_student_id_idx 
      ON $keyspace.students (student_id)
    """)
    
    // Courses table
    session.execute(s"""
      CREATE TABLE IF NOT EXISTS $keyspace.courses (
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
    
    session.execute(s"""
      CREATE INDEX IF NOT EXISTS courses_code_idx 
      ON $keyspace.courses (course_code)
    """)
    
    // Enrollments table
    session.execute(s"""
      CREATE TABLE IF NOT EXISTS $keyspace.enrollments (
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
    
    session.execute(s"""
      CREATE INDEX IF NOT EXISTS enrollments_student_idx 
      ON $keyspace.enrollments (student_id)
    """)
    
    // Risk predictions table
    session.execute(s"""
      CREATE TABLE IF NOT EXISTS $keyspace.risk_predictions (
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
    
    session.execute(s"""
      CREATE INDEX IF NOT EXISTS risk_predictions_student_idx 
      ON $keyspace.risk_predictions (student_id)
    """)
    
    logger.info("All tables created successfully")
  }
  
  def executeAsync(query: String): Future[AsyncResultSet] = {
    val promise = Promise[AsyncResultSet]()
    val resultSet = getSession.executeAsync(query)
    
    resultSet.whenComplete((rs, ex) => {
      if (ex != null) {
        promise.failure(ex)
      } else {
        promise.success(rs)
      }
    })
    
    promise.future
  }
  
  def execute(query: String): Try[ResultSet] = {
    Try(getSession.execute(query))
  }
  
  def close(): Unit = {
    sessionOpt.foreach { session =>
      logger.info("Closing Cassandra session")
      session.close()
    }
    sessionOpt = None
  }
}