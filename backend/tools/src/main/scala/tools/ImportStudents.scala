package tools

import java.net.InetSocketAddress
import java.nio.file.{Files, Paths}
import java.time.Instant
import java.util.UUID

import com.datastax.oss.driver.api.core.CqlSession
import com.datastax.oss.driver.api.core.cql.PreparedStatement
import org.mindrot.jbcrypt.BCrypt

object ImportStudents {

  def usage(): Unit = {
    println("Usage: sbt \"runMain tools.ImportStudents -- --csv <path> [--host <host>] [--port <port>] [--keyspace <ks>] [--username <user>] [--password <pass>]\"")
    System.exit(1)
  }

  def main(rawArgs: Array[String]): Unit = {
    // Expect the args after the sbt runMain separator
    val args = rawArgs.toList
    if (args.isEmpty) usage()

    def nextOpt(map: Map[String, String], list: List[String]): Map[String, String] = list match {
      case Nil => map
      case "--csv" :: value :: tail => nextOpt(map + ("csv" -> value), tail)
      case "--host" :: value :: tail => nextOpt(map + ("host" -> value), tail)
      case "--port" :: value :: tail => nextOpt(map + ("port" -> value), tail)
      case "--keyspace" :: value :: tail => nextOpt(map + ("keyspace" -> value), tail)
      case "--username" :: value :: tail => nextOpt(map + ("username" -> value), tail)
      case "--password" :: value :: tail => nextOpt(map + ("password" -> value), tail)
      case _ => usage(); Map.empty
    }

    val opts = nextOpt(Map.empty, args)
    val csvPath = opts.getOrElse("csv", { println("--csv is required"); usage(); "" })
    val host = opts.getOrElse("host", "localhost")
    val port = opts.getOrElse("port", "9042").toInt
    val keyspace = opts.getOrElse("keyspace", "subjectplanning")
    val username = opts.get("username")
    val password = opts.get("password")

    if (!Files.exists(Paths.get(csvPath))) {
      System.err.println(s"CSV file not found: $csvPath")
      System.exit(2)
    }

    // Build CqlSession
    val builder = CqlSession.builder()
      .addContactPoint(new InetSocketAddress(host, port))
      .withLocalDatacenter("datacenter1")

    val session = (username, password) match {
      case (Some(u), Some(p)) => builder.withAuthCredentials(u, p).build()
      case _ => builder.build()
    }

    try {
      session.execute(s"CREATE KEYSPACE IF NOT EXISTS $keyspace WITH replication = {'class':'SimpleStrategy','replication_factor':1}")
      session.execute(s"USE $keyspace")

      // ensure table exists
      session.execute(s"CREATE TABLE IF NOT EXISTS $keyspace.students (id uuid PRIMARY KEY, student_id text, name text, email text, password_hash text, gpa double, semester int, created_at timestamp, updated_at timestamp)")

      val insertCql = s"INSERT INTO $keyspace.students (id, student_id, name, email, password_hash, gpa, semester, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
      val prepared: PreparedStatement = session.prepare(insertCql)

      val reader = scala.io.Source.fromFile(csvPath)
      try {
        val lines = reader.getLines().toList
        if (lines.isEmpty) {
          println("Empty CSV")
          System.exit(0)
        }

        val header = lines.head.split(',').map(_.trim.toLowerCase)
        val rows = lines.tail

        def idx(name: String): Int = header.indexOf(name)

        rows.foreach { line =>
          val cols = line.split(',').map(_.trim)
          val studentId = if (idx("student_id") >= 0) cols(idx("student_id")) else ""
          val name = if (idx("name") >= 0) cols(idx("name")) else ""
          val email = if (idx("email") >= 0) cols(idx("email")) else ""
          val plainPassword = if (idx("password") >= 0) cols(idx("password")) else ""
          val gpa = if (idx("gpa") >= 0) cols(idx("gpa")) match { case s if s.nonEmpty => s.toDouble; case _ => 0.0 } else 0.0
          val semester = if (idx("semester") >= 0) cols(idx("semester")) match { case s if s.nonEmpty => s.toInt; case _ => 1 } else 1

          val passwordHash = if (plainPassword.nonEmpty) BCrypt.hashpw(plainPassword, BCrypt.gensalt()) else ""
          val id = UUID.randomUUID()
          val now = Instant.now()

          session.execute(prepared.bind(id, studentId, name, email, passwordHash, Double.box(gpa), Int.box(semester), now, now))
          println(s"Inserted $email")
        }
      } finally reader.close()

    } finally {
      session.close()
    }

    println("Done")
  }
}
