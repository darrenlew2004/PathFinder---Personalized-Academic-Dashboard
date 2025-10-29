package controllers

import models._
import repositories.StudentRepository
import services.JWTService
import javax.inject._
import play.api.mvc._
import play.api.libs.json._
import scala.concurrent.{ExecutionContext, Future}
import org.mindrot.jbcrypt.BCrypt
import play.api.Logger

@Singleton
class AuthController @Inject()(
  cc: ControllerComponents,
  studentRepository: StudentRepository,
  jwtService: JWTService
)(implicit ec: ExecutionContext) extends AbstractController(cc) {
  
  private val logger = Logger(this.getClass)
  
  def login(): Action[JsValue] = Action.async(parse.json) { request =>
    request.body.validate[LoginRequest].fold(
      errors => {
        logger.warn(s"Invalid login request: $errors")
        Future.successful(BadRequest(Json.obj(
          "error" -> "Invalid request format",
          "details" -> JsError.toJson(errors)
        )))
      },
      loginRequest => {
        studentRepository.findByEmail(loginRequest.email).flatMap {
          case Some(student) =>
            if (BCrypt.checkpw(loginRequest.password, student.passwordHash)) {
              val token = jwtService.generateToken(student.id, student.email)
              val response = LoginResponse(token, student)
              logger.info(s"User logged in: ${student.email}")
              Future.successful(Ok(Json.toJson(response)))
            } else {
              logger.warn(s"Invalid password for: ${loginRequest.email}")
              Future.successful(Unauthorized(Json.obj(
                "error" -> "Invalid email or password"
              )))
            }
          case None =>
            logger.warn(s"User not found: ${loginRequest.email}")
            Future.successful(Unauthorized(Json.obj(
              "error" -> "Invalid email or password"
            )))
        }.recover {
          case e: Exception =>
            logger.error(s"Login error: ${e.getMessage}", e)
            InternalServerError(Json.obj(
              "error" -> "An error occurred during login"
            ))
        }
      }
    )
  }
  
  def logout(): Action[AnyContent] = Action { request =>
    // For JWT, logout is handled client-side by removing the token
    logger.info("User logged out")
    Ok(Json.obj("message" -> "Logged out successfully"))
  }
  
  def verifyToken(): Action[AnyContent] = Action { request =>
    request.headers.get("Authorization") match {
      case Some(authHeader) if authHeader.startsWith("Bearer ") =>
        val token = authHeader.substring(7)
        jwtService.validateToken(token) match {
          case Some(claims) =>
            Ok(Json.obj(
              "valid" -> true,
              "userId" -> claims.userId.toString,
              "email" -> claims.email
            ))
          case None =>
            Unauthorized(Json.obj("valid" -> false, "error" -> "Invalid token"))
        }
      case _ =>
        Unauthorized(Json.obj("valid" -> false, "error" -> "No token provided"))
    }
  }
  
  def register(): Action[JsValue] = Action.async(parse.json) { request =>
    val studentResult = for {
      studentId <- (request.body \ "studentId").validate[String]
      name <- (request.body \ "name").validate[String]
      email <- (request.body \ "email").validate[String]
      password <- (request.body \ "password").validate[String]
      gpa <- (request.body \ "gpa").validateOpt[Double].map(_.getOrElse(0.0))
      semester <- (request.body \ "semester").validateOpt[Int].map(_.getOrElse(1))
    } yield (studentId, name, email, password, gpa, semester)
    
    studentResult.fold(
      errors => {
        logger.warn(s"Invalid registration request: $errors")
        Future.successful(BadRequest(Json.obj(
          "error" -> "Invalid request format",
          "details" -> JsError.toJson(errors)
        )))
      },
      { case (studentId, name, email, password, gpa, semester) =>
        studentRepository.findByEmail(email).flatMap {
          case Some(_) =>
            Future.successful(BadRequest(Json.obj(
              "error" -> "Email already registered"
            )))
          case None =>
            val hashedPassword = BCrypt.hashpw(password, BCrypt.gensalt())
            val now = java.time.Instant.now()
            val student = Student(
              id = java.util.UUID.randomUUID(),
              studentId = studentId,
              name = name,
              email = email,
              passwordHash = hashedPassword,
              gpa = gpa,
              semester = semester,
              createdAt = now,
              updatedAt = now
            )
            
            studentRepository.create(student).map { createdStudent =>
              val token = jwtService.generateToken(createdStudent.id, createdStudent.email)
              val response = LoginResponse(token, createdStudent)
              logger.info(s"User registered: ${createdStudent.email}")
              Created(Json.toJson(response))
            }.recover {
              case e: Exception =>
                logger.error(s"Registration error: ${e.getMessage}", e)
                InternalServerError(Json.obj(
                  "error" -> "An error occurred during registration"
                ))
            }
        }
      }
    )
  }
}