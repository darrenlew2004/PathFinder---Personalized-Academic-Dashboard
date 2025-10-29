package controllers

import models._
import repositories._
import services.{JWTService, RiskPredictionService}
import javax.inject._
import play.api.mvc._
import play.api.libs.json._
import scala.concurrent.{ExecutionContext, Future}
import java.util.UUID
import scala.util.{Try, Success, Failure}
import play.api.Logger

@Singleton
class StudentStatsController @Inject()(
  cc: ControllerComponents,
  studentRepository: StudentRepository,
  enrollmentRepository: EnrollmentRepository,
  courseRepository: CourseRepository,
  riskPredictionService: RiskPredictionService,
  jwtService: JWTService
)(implicit ec: ExecutionContext) extends AbstractController(cc) {
  
  private val logger = Logger(this.getClass)
  
  private def authenticateRequest(request: Request[_]): Option[UUID] = {
    request.headers.get("Authorization").flatMap { authHeader =>
      if (authHeader.startsWith("Bearer ")) {
        val token = authHeader.substring(7)
        jwtService.validateToken(token).map(_.userId)
      } else None
    }
  }
  
  def getStudentStats(studentId: String): Action[AnyContent] = Action.async { request =>
    authenticateRequest(request) match {
      case Some(userId) =>
        Try(UUID.fromString(studentId)) match {
          case Success(id) =>
            fetchStudentStats(id).map { stats =>
              Ok(Json.toJson(stats))
            }.recover {
              case e: Exception =>
                logger.error(s"Error fetching student stats: ${e.getMessage}", e)
                InternalServerError(Json.obj("error" -> "Failed to fetch student statistics"))
            }
          case Failure(_) =>
            Future.successful(BadRequest(Json.obj("error" -> "Invalid student ID format")))
        }
      case None =>
        Future.successful(Unauthorized(Json.obj("error" -> "Authentication required")))
    }
  }
  
  def getCurrentStudent(): Action[AnyContent] = Action.async { request =>
    authenticateRequest(request) match {
      case Some(userId) =>
        fetchStudentStats(userId).map { stats =>
          Ok(Json.toJson(stats))
        }.recover {
          case e: Exception =>
            logger.error(s"Error fetching current student: ${e.getMessage}", e)
            InternalServerError(Json.obj("error" -> "Failed to fetch student data"))
        }
      case None =>
        Future.successful(Unauthorized(Json.obj("error" -> "Authentication required")))
    }
  }
  
  def getRiskPredictions(studentId: String): Action[AnyContent] = Action.async { request =>
    authenticateRequest(request) match {
      case Some(userId) =>
        Try(UUID.fromString(studentId)) match {
          case Success(id) =>
            riskPredictionService.predictRisksForStudent(id).map { predictions =>
              Ok(Json.toJson(predictions))
            }.recover {
              case e: Exception =>
                logger.error(s"Error fetching risk predictions: ${e.getMessage}", e)
                InternalServerError(Json.obj("error" -> "Failed to fetch risk predictions"))
            }
          case Failure(_) =>
            Future.successful(BadRequest(Json.obj("error" -> "Invalid student ID format")))
        }
      case None =>
        Future.successful(Unauthorized(Json.obj("error" -> "Authentication required")))
    }
  }
  
  def getCourseProgress(studentId: String): Action[AnyContent] = Action.async { request =>
    authenticateRequest(request) match {
      case Some(userId) =>
        Try(UUID.fromString(studentId)) match {
          case Success(id) =>
            fetchCourseProgress(id).map { progress =>
              Ok(Json.toJson(progress))
            }.recover {
              case e: Exception =>
                logger.error(s"Error fetching course progress: ${e.getMessage}", e)
                InternalServerError(Json.obj("error" -> "Failed to fetch course progress"))
            }
          case Failure(_) =>
            Future.successful(BadRequest(Json.obj("error" -> "Invalid student ID format")))
        }
      case None =>
        Future.successful(Unauthorized(Json.obj("error" -> "Authentication required")))
    }
  }
  
  private def fetchStudentStats(studentId: UUID): Future[StudentStats] = {
    for {
      studentOpt <- studentRepository.findById(studentId)
      student = studentOpt.getOrElse(throw new Exception("Student not found"))
      enrollments <- enrollmentRepository.findByStudentId(studentId)
      currentEnrollments = enrollments.filter(_.status == CourseStatus.ENROLLED)
      courseIds = currentEnrollments.map(_.courseId)
      courses <- courseRepository.findByIds(courseIds)
      riskPredictions <- riskPredictionService.predictRisksForStudent(studentId)
      completedCount <- enrollmentRepository.getCompletedCount(studentId)
      totalCredits <- enrollmentRepository.getTotalCredits(studentId)
      avgAttendance <- enrollmentRepository.getAverageAttendance(studentId)
    } yield {
      val courseProgress = currentEnrollments.flatMap { enrollment =>
        courses.find(_.id == enrollment.courseId).map { course =>
          val risk = riskPredictions.find(_.courseId == course.id)
          CourseProgress(course, enrollment, risk)
        }
      }
      
      val riskDistribution = riskPredictions.groupBy(_.riskLevel.toString).view.mapValues(_.size).toMap
      
      StudentStats(
        student = student,
        currentCourses = courseProgress,
        completedCourses = completedCount,
        totalCredits = totalCredits,
        averageAttendance = avgAttendance,
        riskDistribution = riskDistribution
      )
    }
  }
  
  private def fetchCourseProgress(studentId: UUID): Future[List[CourseProgress]] = {
    for {
      enrollments <- enrollmentRepository.findByStudentId(studentId)
      currentEnrollments = enrollments.filter(_.status == CourseStatus.ENROLLED)
      courseIds = currentEnrollments.map(_.courseId)
      courses <- courseRepository.findByIds(courseIds)
      riskPredictions <- riskPredictionService.predictRisksForStudent(studentId)
    } yield {
      currentEnrollments.flatMap { enrollment =>
        courses.find(_.id == enrollment.courseId).map { course =>
          val risk = riskPredictions.find(_.courseId == course.id)
          CourseProgress(course, enrollment, risk)
        }
      }
    }
  }
}