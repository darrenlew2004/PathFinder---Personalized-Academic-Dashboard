package repositories

import com.datastax.oss.driver.api.core.cql.Row
import models._
import services.CassandraService
import javax.inject._
import scala.concurrent.{ExecutionContext, Future}
import scala.jdk.CollectionConverters._
import java.time.Instant
import java.util.UUID
import play.api.Logger

@Singleton
class StudentRepository @Inject()(
  cassandra: CassandraService
)(implicit ec: ExecutionContext) {
  
  private val logger = Logger(this.getClass)
  private val keyspace = "subjectplanning"
  
  def findByEmail(email: String): Future[Option[Student]] = {
    val query = s"""
      SELECT * FROM $keyspace.students 
      WHERE email = '$email' 
      ALLOW FILTERING
    """
    
    cassandra.executeAsync(query).map { resultSet =>
      val row = resultSet.one()
      if (row != null) Some(mapRowToStudent(row))
      else None
    }.recover {
      case e: Exception =>
        logger.error(s"Error finding student by email: ${e.getMessage}", e)
        None
    }
  }
  
  def findById(id: UUID): Future[Option[Student]] = {
    val query = s"""
      SELECT * FROM $keyspace.students 
      WHERE id = $id
    """
    
    cassandra.executeAsync(query).map { resultSet =>
      val row = resultSet.one()
      if (row != null) Some(mapRowToStudent(row))
      else None
    }.recover {
      case e: Exception =>
        logger.error(s"Error finding student by id: ${e.getMessage}", e)
        None
    }
  }
  
  def findByStudentId(studentId: String): Future[Option[Student]] = {
    val query = s"""
      SELECT * FROM $keyspace.students 
      WHERE student_id = '$studentId' 
      ALLOW FILTERING
    """
    
    cassandra.executeAsync(query).map { resultSet =>
      val row = resultSet.one()
      if (row != null) Some(mapRowToStudent(row))
      else None
    }.recover {
      case e: Exception =>
        logger.error(s"Error finding student by student_id: ${e.getMessage}", e)
        None
    }
  }
  
  def create(student: Student): Future[Student] = {
    val query = s"""
      INSERT INTO $keyspace.students 
      (id, student_id, name, email, password_hash, gpa, semester, created_at, updated_at)
      VALUES (
        ${student.id},
        '${student.studentId}',
        '${student.name}',
        '${student.email}',
        '${student.passwordHash}',
        ${student.gpa},
        ${student.semester},
        '${student.createdAt}',
        '${student.updatedAt}'
      )
    """
    
    cassandra.executeAsync(query).map { _ =>
      logger.info(s"Created student: ${student.email}")
      student
    }.recover {
      case e: Exception =>
        logger.error(s"Error creating student: ${e.getMessage}", e)
        throw e
    }
  }
  
  def update(student: Student): Future[Student] = {
    val query = s"""
      UPDATE $keyspace.students 
      SET name = '${student.name}',
          gpa = ${student.gpa},
          semester = ${student.semester},
          updated_at = '${Instant.now()}'
      WHERE id = ${student.id}
    """
    
    cassandra.executeAsync(query).map { _ =>
      logger.info(s"Updated student: ${student.id}")
      student.copy(updatedAt = Instant.now())
    }.recover {
      case e: Exception =>
        logger.error(s"Error updating student: ${e.getMessage}", e)
        throw e
    }
  }
  
  def delete(id: UUID): Future[Boolean] = {
    val query = s"""
      DELETE FROM $keyspace.students 
      WHERE id = $id
    """
    
    cassandra.executeAsync(query).map { _ =>
      logger.info(s"Deleted student: $id")
      true
    }.recover {
      case e: Exception =>
        logger.error(s"Error deleting student: ${e.getMessage}", e)
        false
    }
  }
  
  def findAll(): Future[List[Student]] = {
    val query = s"SELECT * FROM $keyspace.students"
    
    cassandra.executeAsync(query).map { resultSet =>
      resultSet.currentPage().asScala.map(mapRowToStudent).toList
    }.recover {
      case e: Exception =>
        logger.error(s"Error finding all students: ${e.getMessage}", e)
        List.empty
    }
  }
  
  private def mapRowToStudent(row: Row): Student = {
    Student(
      id = row.getUuid("id"),
      studentId = row.getString("student_id"),
      name = row.getString("name"),
      email = row.getString("email"),
      passwordHash = row.getString("password_hash"),
      gpa = row.getDouble("gpa"),
      semester = row.getInt("semester"),
      createdAt = row.getInstant("created_at"),
      updatedAt = row.getInstant("updated_at")
    )
  }
}