"""
Test Cassandra connection and permissions
Run this to check what you can do with your current credentials
"""

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy
import sys

# Your current credentials
CASSANDRA_HOST = "sunway.hep88.com"
CASSANDRA_PORT = 9042
CASSANDRA_KEYSPACE = "subjectplanning"
CASSANDRA_DATACENTER = "datacenter1"
CASSANDRA_USERNAME = "planusertest"
CASSANDRA_PASSWORD = "Ic7cU8K965Zqx"

print(f"🔍 Testing connection to {CASSANDRA_HOST}:{CASSANDRA_PORT}")
print(f"   Keyspace: {CASSANDRA_KEYSPACE}")
print(f"   User: {CASSANDRA_USERNAME}\n")

try:
    # Connect
    auth_provider = PlainTextAuthProvider(
        username=CASSANDRA_USERNAME,
        password=CASSANDRA_PASSWORD
    )
    
    from cassandra.io.geventreactor import GeventConnection
    from gevent import monkey
    monkey.patch_all()
    
    cluster = Cluster(
        contact_points=[CASSANDRA_HOST],
        port=CASSANDRA_PORT,
        auth_provider=auth_provider,
        protocol_version=4,
        load_balancing_policy=DCAwareRoundRobinPolicy(local_dc=CASSANDRA_DATACENTER)
    )
    
    session = cluster.connect()
    session.set_keyspace(CASSANDRA_KEYSPACE)
    
    print("✅ Connection successful!\n")
    
    # Check what tables exist
    print("📋 Checking existing tables...")
    result = session.execute(
        "SELECT table_name FROM system_schema.tables WHERE keyspace_name = %s",
        (CASSANDRA_KEYSPACE,)
    )
    
    tables = [row.table_name for row in result]
    
    if tables:
        print(f"   Found {len(tables)} table(s):")
        for table in tables:
            print(f"   - {table}")
    else:
        print("   ⚠️  No tables found in this keyspace")
    
    print("\n📝 Testing CREATE permission...")
    try:
        # Try to create a test table
        session.execute("""
            CREATE TABLE IF NOT EXISTS test_permissions (
                id UUID PRIMARY KEY,
                test_field TEXT
            )
        """)
        print("   ✅ CREATE permission: YES")
        
        # Clean up
        session.execute("DROP TABLE IF EXISTS test_permissions")
        print("   ✅ DROP permission: YES")
        
    except Exception as e:
        if "Unauthorized" in str(e) or "permission" in str(e).lower():
            print(f"   ❌ CREATE permission: NO")
            print(f"   Error: {e}")
            print("\n⚠️  You need CREATE permissions to set up your database.")
            print("   Contact your supervisor to:")
            print("   1. Grant you CREATE permissions, OR")
            print("   2. Run the schema.cql file for you")
        else:
            print(f"   ❌ Unexpected error: {e}")
    
    print("\n📝 Testing SELECT permission...")
    try:
        # Try to query system tables
        session.execute("SELECT * FROM system.local LIMIT 1")
        print("   ✅ SELECT permission: YES")
    except Exception as e:
        print(f"   ❌ SELECT permission: NO - {e}")
    
    cluster.shutdown()
    print("\n✅ Test complete!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)
