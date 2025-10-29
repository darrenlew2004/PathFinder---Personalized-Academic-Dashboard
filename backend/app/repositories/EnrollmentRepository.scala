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
class EnrollmentRepository @Inject()(
  cassandra: CassandraService
)(implicit ec: ExecutionContext) {
  
  private val logger = Logger(this.getClass)
  private val keyspace = "subjectplanning"
  
  def findByStudentId(studentId: UUID): Future[List[Enrollment]] = {
    val query = s"""
      SELECT * FROM $keyspace.enrollments 
      WHERE student_id = $studentId 
      ALLOW FILTERING
    """
    
    cassandra.executeAsync(query).map { resultSet =>
      resultSet.currentPage().asScala.map(mapRowToEnrollment).toList
    }.recover {
      case e: Exception =>
        logger.error(s"Error finding enrollments: ${e.getMessage}", e)
        List.empty
    }
  }
  
  def findByStudentAndSemester(studentId: UUID, semester: Int): Future[List[Enrollment]] = {
    val query = s"""
      SELECT * FROM $keyspace.enrollments 
      WHERE student_id = $studentId AND semester = $semester 
      ALLOW FILTERING
    """
    
    cassandra.executeAsync(query).map { resultSet =>
      resultSet.currentPage().asScala.map(mapRowToEnrollment).toList
    }.recover {
      case e: Exception =>
        logger.error(s"Error finding enrollments by semester: ${e.getMessage}", e)
        List.empty
    }
  }
  
  def findById(id: UUID): Future[Option[Enrollment]] = {
    val query = s"""
      SELECT * FROM $keyspace.enrollments 
      WHERE id = $id
    """
    
    cassandra.executeAsync(query).map { resultSet =>
      val row = resultSet.one()
      if (row != null) Some(mapRowToEnrollment(row))
      else None
    }.recover {
      case e: Exception =>
        logger.error(s"Error finding enrollment: ${e.getMessage}", e)
        None
    }
  }
  
  def create(enrollment: Enrollment): Future[Enrollment] = {
    val completedAtStr = enrollment.completedAt.map(t => s"'$t'").getOrElse("null")
    val gradeStr = enrollment.grade.map(g => s"'$g'").getOrElse("null")
    
    val query = s"""
      INSERT INTO $keyspace.enrollments 
      (id, student_id, course_id, semester, grade, status, attendance_rate, enrolled_at, completed_at)
      VALUES (
        ${enrollment.id},
        ${enrollment.studentId},
        ${enrollment.courseId},
        ${enrollment.semester},
        $gradeStr,
        '${enrollment.status}',
        ${enrollment.attendanceRate},
        '${enrollment.enrolledAt}',
        $completedAtStr
      )
    """
    
    cassandra.executeAsync(query).map { _ =>
      logger.info(s"Created enrollment: ${enrollment.id}")
      enrollment
    }.recover {
      case e: Exception =>
        logger.error(s"Error creating enrollment: ${e.getMessage}", e)
        throw e
    }
  }
  
  def update(enrollment: Enrollment): Future[Enrollment] = {
    val gradeStr = enrollment.grade.map(g => s"'$g'").getOrElse("null")
    val completedAtStr = enrollment.completedAt.map(t => s"'$t'").getOrElse("null")
    
    val query = s"""
      UPDATE $keyspace.enrollments 
      SET grade = $gradeStr,
          status = '${enrollment.status}',
          attendance_rate = ${enrollment.attendanceRate},
          completed_at = $completedAtStr
      WHERE id = ${enrollment.id}
    """
    
    cassandra.executeAsync(query).map { _ =>
      logger.info(s"Updated enrollment: ${enrollment.id}")
      enrollment
    }.recover {
      case e: Exception =>
        logger.error(s"Error updating enrollment: ${e.getMessage}", e)
        throw e
    }
  }
  
  def getCompletedCount(studentId: UUID): Future[Int] = {
    findByStudentId(studentId).map { enrollments =>
      enrollments.count(e => e.status == CourseStatus.COMPLETED)
    }
  }
  
  def getTotalCredits(studentId: UUID): Future[Int] = {
    // This would need to join with courses - simplified here
    findByStudentId(studentId).map { enrollments =>
      enrollments.count(_.status == CourseStatus.COMPLETED) * 3 // Assuming 3 credits per course
    }
  }
  
  def getAverageAttendance(studentId: UUID): Future[Double] = {
    findByStudentId(studentId).map { enrollments =>
      if (enrollments.isEmpty) 0.0
      else enrollments.map(_.attendanceRate).sum / enrollments.length
    }
  }
  
  private def mapRowToEnrollment(row: Row): Enrollment = {
    Enrollment(
      id = row.getUuid("id"),
      studentId = row.getUuid("student_id"),
      courseId = row.getUuid("course_id"),
      semester = row.getInt("semester"),
      grade = Option(row.getString("grade")),
      status = CourseStatus.withName(row.getString("status")),
      attendanceRate = row.getDouble("attendance_rate"),
      enrolledAt = row.getInstant("enrolled_at"),
      completedAt = Option(row.getInstant("completed_at"))
    )
  }
}