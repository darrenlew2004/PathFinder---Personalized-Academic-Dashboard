package controllers

import services.CassandraService
import javax.inject._
import play.api.mvc._
import play.api.libs.json._
import scala.concurrent.{ExecutionContext, Future}
import scala.util.{Try, Success, Failure}

@Singleton
class HealthController @Inject()(
  cc: ControllerComponents,
  cassandra: CassandraService
)(implicit ec: ExecutionContext) extends AbstractController(cc) {
  
  def health(): Action[AnyContent] = Action.async {
    checkCassandraConnection().map { isConnected =>
      val status = if (isConnected) "healthy" else "unhealthy"
      val httpStatus = if (isConnected) Ok else ServiceUnavailable
      
      httpStatus(Json.obj(
        "status" -> status,
        "cassandra" -> isConnected,
        "timestamp" -> java.time.Instant.now().toString
      ))
    }.recover {
      case e: Exception =>
        ServiceUnavailable(Json.obj(
          "status" -> "unhealthy",
          "error" -> e.getMessage,
          "timestamp" -> java.time.Instant.now().toString
        ))
    }
  }
  
  private def checkCassandraConnection(): Future[Boolean] = Future {
    Try {
      val session = cassandra.getSession
      val result = session.execute("SELECT release_version FROM system.local")
      result.one() != null
    } match {
      case Success(value) => value
      case Failure(_) => false
    }
  }
}