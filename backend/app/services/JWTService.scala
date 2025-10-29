package services

import com.auth0.jwt.JWT
import com.auth0.jwt.algorithms.Algorithm
import com.auth0.jwt.exceptions.JWTVerificationException
import javax.inject._
import play.api.Configuration
import java.util.{Date, UUID}
import scala.util.{Try, Success, Failure}
import play.api.Logger

case class JWTClaims(userId: UUID, email: String)

@Singleton
class JWTService @Inject()(config: Configuration) {
  
  private val logger = Logger(this.getClass)
  private val secret = config.get[String]("jwt.secret")
  private val expirationTime = config.getOptional[Int]("jwt.expirationHours").getOrElse(24)
  private val algorithm = Algorithm.HMAC256(secret)
  
  def generateToken(userId: UUID, email: String): String = {
    val now = new Date()
    val expiresAt = new Date(now.getTime + (expirationTime * 60 * 60 * 1000))
    
    JWT.create()
      .withIssuer("student-risk-prediction")
      .withSubject(userId.toString)
      .withClaim("email", email)
      .withIssuedAt(now)
      .withExpiresAt(expiresAt)
      .sign(algorithm)
  }
  
  def validateToken(token: String): Option[JWTClaims] = {
    Try {
      val verifier = JWT.require(algorithm)
        .withIssuer("student-risk-prediction")
        .build()
      
      val decodedJWT = verifier.verify(token)
      val userId = UUID.fromString(decodedJWT.getSubject)
      val email = decodedJWT.getClaim("email").asString()
      
      JWTClaims(userId, email)
    } match {
      case Success(claims) => Some(claims)
      case Failure(e: JWTVerificationException) =>
        logger.warn(s"Invalid JWT token: ${e.getMessage}")
        None
      case Failure(e) =>
        logger.error(s"Error validating token: ${e.getMessage}", e)
        None
    }
  }
  
  def refreshToken(oldToken: String): Option[String] = {
    validateToken(oldToken).map { claims =>
      generateToken(claims.userId, claims.email)
    }
  }
}