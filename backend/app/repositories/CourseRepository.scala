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
class CourseRepository @Inject()(
  cassandra: CassandraService
)(implicit ec: ExecutionContext) {
  
  private val logger = Logger(this.getClass)
  private val keyspace = "subjectplanning"
  
  def findById(id: UUID): Future[Option[Course]] = {
    val query = s"""
      SELECT * FROM $keyspace.courses 
      WHERE id = $id
    """
    
    cassandra.executeAsync(query).map { resultSet =>
      val row = resultSet.one()
      if (row != null) Some(mapRowToCourse(row))
      else None
    }.recover {
      case e: Exception =>
        logger.error(s"Error finding course: ${e.getMessage}", e)
        None
    }
  }
  
  def findByCourseCode(courseCode: String): Future[Option[Course]] = {
    val query = s"""
      SELECT * FROM $keyspace.courses 
      WHERE course_code = '$courseCode' 
      ALLOW FILTERING
    """
    
    cassandra.executeAsync(query).map { resultSet =>
      val row = resultSet.one()
      if (row != null) Some(mapRowToCourse(row))
      else None
    }.recover {
      case e: Exception =>
        logger.error(s"Error finding course by code: ${e.getMessage}", e)
        None
    }
  }
  
  def findAll(): Future[List[Course]] = {
    val query = s"SELECT * FROM $keyspace.courses"
    
    cassandra.executeAsync(query).map { resultSet =>
      resultSet.currentPage().asScala.map(mapRowToCourse).toList
    }.recover {
      case e: Exception =>
        logger.error(s"Error finding all courses: ${e.getMessage}", e)
        List.empty
    }
  }
  
  def create(course: Course): Future[Course] = {
    val prerequisitesStr = course.prerequisites.map(p => s"'$p'").mkString("[", ",", "]")
    
    val query = s"""
      INSERT INTO $keyspace.courses 
      (id, course_code, course_name, credits, difficulty, prerequisites, description, created_at)
      VALUES (
        ${course.id},
        '${course.courseCode}',
        '${course.courseName.replace("'", "''")}',
        ${course.credits},
        ${course.difficulty},
        $prerequisitesStr,
        '${course.description.replace("'", "''")}',
        '${course.createdAt}'
      )
    """
    
    cassandra.executeAsync(query).map { _ =>
      logger.info(s"Created course: ${course.courseCode}")
      course
    }.recover {
      case e: Exception =>
        logger.error(s"Error creating course: ${e.getMessage}", e)
        throw e
    }
  }
  
  def update(course: Course): Future[Course] = {
    val prerequisitesStr = course.prerequisites.map(p => s"'$p'").mkString("[", ",", "]")
    
    val query = s"""
      UPDATE $keyspace.courses 
      SET course_name = '${course.courseName.replace("'", "''")}',
          credits = ${course.credits},
          difficulty = ${course.difficulty},
          prerequisites = $prerequisitesStr,
          description = '${course.description.replace("'", "''")}'
      WHERE id = ${course.id}
    """
    
    cassandra.executeAsync(query).map { _ =>
      logger.info(s"Updated course: ${course.id}")
      course
    }.recover {
      case e: Exception =>
        logger.error(s"Error updating course: ${e.getMessage}", e)
        throw e
    }
  }
  
  def delete(id: UUID): Future[Boolean] = {
    val query = s"""
      DELETE FROM $keyspace.courses 
      WHERE id = $id
    """
    
    cassandra.executeAsync(query).map { _ =>
      logger.info(s"Deleted course: $id")
      true
    }.recover {
      case e: Exception =>
        logger.error(s"Error deleting course: ${e.getMessage}", e)
        false
    }
  }
  
  def findByIds(ids: List[UUID]): Future[List[Course]] = {
    if (ids.isEmpty) return Future.successful(List.empty)
    
    val idsStr = ids.mkString(",")
    val query = s"""
      SELECT * FROM $keyspace.courses 
      WHERE id IN ($idsStr)
    """
    
    cassandra.executeAsync(query).map { resultSet =>
      resultSet.currentPage().asScala.map(mapRowToCourse).toList
    }.recover {
      case e: Exception =>
        logger.error(s"Error finding courses by ids: ${e.getMessage}", e)
        List.empty
    }
  }
  
  private def mapRowToCourse(row: Row): Course = {
    val prerequisitesList = row.getList("prerequisites", classOf[String])
    
    Course(
      id = row.getUuid("id"),
      courseCode = row.getString("course_code"),
      courseName = row.getString("course_name"),
      credits = row.getInt("credits"),
      difficulty = row.getDouble("difficulty"),
      prerequisites = if (prerequisitesList != null) prerequisitesList.asScala.toList else List.empty,
      description = row.getString("description"),
      createdAt = row.getInstant("created_at")
    )
  }
}