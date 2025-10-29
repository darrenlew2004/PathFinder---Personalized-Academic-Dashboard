// @GENERATOR:play-routes-compiler
// @SOURCE:conf/routes

package router

import play.core.routing._
import play.core.routing.HandlerInvokerFactory._

import play.api.mvc._

import _root_.controllers.Assets.Asset

class Routes(
  override val errorHandler: play.api.http.HttpErrorHandler, 
  // @LINE:5
  AuthController_0: controllers.AuthController,
  // @LINE:11
  StudentStatsController_1: controllers.StudentStatsController,
  // @LINE:17
  HealthController_2: controllers.HealthController,
  // @LINE:20
  Assets_3: controllers.Assets,
  val prefix: String
) extends GeneratedRouter {

  @javax.inject.Inject()
  def this(errorHandler: play.api.http.HttpErrorHandler,
    // @LINE:5
    AuthController_0: controllers.AuthController,
    // @LINE:11
    StudentStatsController_1: controllers.StudentStatsController,
    // @LINE:17
    HealthController_2: controllers.HealthController,
    // @LINE:20
    Assets_3: controllers.Assets
  ) = this(errorHandler, AuthController_0, StudentStatsController_1, HealthController_2, Assets_3, "/")

  def withPrefix(addPrefix: String): Routes = {
    val prefix = play.api.routing.Router.concatPrefix(addPrefix, this.prefix)
    router.RoutesPrefix.setPrefix(prefix)
    new Routes(errorHandler, AuthController_0, StudentStatsController_1, HealthController_2, Assets_3, prefix)
  }

  private val defaultPrefix: String = {
    if (this.prefix.endsWith("/")) "" else "/"
  }

  def documentation = List(
    ("""POST""", this.prefix + (if(this.prefix.endsWith("/")) "" else "/") + """auth/login""", """controllers.AuthController.login"""),
    ("""POST""", this.prefix + (if(this.prefix.endsWith("/")) "" else "/") + """auth/logout""", """controllers.AuthController.logout"""),
    ("""POST""", this.prefix + (if(this.prefix.endsWith("/")) "" else "/") + """auth/register""", """controllers.AuthController.register"""),
    ("""GET""", this.prefix + (if(this.prefix.endsWith("/")) "" else "/") + """auth/verify""", """controllers.AuthController.verifyToken"""),
    ("""GET""", this.prefix + (if(this.prefix.endsWith("/")) "" else "/") + """api/students/current""", """controllers.StudentStatsController.getCurrentStudent"""),
    ("""GET""", this.prefix + (if(this.prefix.endsWith("/")) "" else "/") + """api/students/""" + "$" + """id<[^/]+>/stats""", """controllers.StudentStatsController.getStudentStats(id:String)"""),
    ("""GET""", this.prefix + (if(this.prefix.endsWith("/")) "" else "/") + """api/students/""" + "$" + """id<[^/]+>/progress""", """controllers.StudentStatsController.getCourseProgress(id:String)"""),
    ("""GET""", this.prefix + (if(this.prefix.endsWith("/")) "" else "/") + """api/students/""" + "$" + """id<[^/]+>/risks""", """controllers.StudentStatsController.getRiskPredictions(id:String)"""),
    ("""GET""", this.prefix + (if(this.prefix.endsWith("/")) "" else "/") + """health""", """controllers.HealthController.health"""),
    ("""GET""", this.prefix + (if(this.prefix.endsWith("/")) "" else "/") + """assets/""" + "$" + """file<.+>""", """controllers.Assets.versioned(path:String = "/public", file:Asset)"""),
    Nil
  ).foldLeft(Seq.empty[(String, String, String)]) { (s,e) => e.asInstanceOf[Any] match {
    case r @ (_,_,_) => s :+ r.asInstanceOf[(String, String, String)]
    case l => s ++ l.asInstanceOf[List[(String, String, String)]]
  }}


  // @LINE:5
  private lazy val controllers_AuthController_login0_route = Route("POST",
    PathPattern(List(StaticPart(this.prefix), StaticPart(this.defaultPrefix), StaticPart("auth/login")))
  )
  private lazy val controllers_AuthController_login0_invoker = createInvoker(
    AuthController_0.login,
    play.api.routing.HandlerDef(this.getClass.getClassLoader,
      "router",
      "controllers.AuthController",
      "login",
      Nil,
      "POST",
      this.prefix + """auth/login""",
      """ Authentication""",
      Seq()
    )
  )

  // @LINE:6
  private lazy val controllers_AuthController_logout1_route = Route("POST",
    PathPattern(List(StaticPart(this.prefix), StaticPart(this.defaultPrefix), StaticPart("auth/logout")))
  )
  private lazy val controllers_AuthController_logout1_invoker = createInvoker(
    AuthController_0.logout,
    play.api.routing.HandlerDef(this.getClass.getClassLoader,
      "router",
      "controllers.AuthController",
      "logout",
      Nil,
      "POST",
      this.prefix + """auth/logout""",
      """""",
      Seq()
    )
  )

  // @LINE:7
  private lazy val controllers_AuthController_register2_route = Route("POST",
    PathPattern(List(StaticPart(this.prefix), StaticPart(this.defaultPrefix), StaticPart("auth/register")))
  )
  private lazy val controllers_AuthController_register2_invoker = createInvoker(
    AuthController_0.register,
    play.api.routing.HandlerDef(this.getClass.getClassLoader,
      "router",
      "controllers.AuthController",
      "register",
      Nil,
      "POST",
      this.prefix + """auth/register""",
      """""",
      Seq()
    )
  )

  // @LINE:8
  private lazy val controllers_AuthController_verifyToken3_route = Route("GET",
    PathPattern(List(StaticPart(this.prefix), StaticPart(this.defaultPrefix), StaticPart("auth/verify")))
  )
  private lazy val controllers_AuthController_verifyToken3_invoker = createInvoker(
    AuthController_0.verifyToken,
    play.api.routing.HandlerDef(this.getClass.getClassLoader,
      "router",
      "controllers.AuthController",
      "verifyToken",
      Nil,
      "GET",
      this.prefix + """auth/verify""",
      """""",
      Seq()
    )
  )

  // @LINE:11
  private lazy val controllers_StudentStatsController_getCurrentStudent4_route = Route("GET",
    PathPattern(List(StaticPart(this.prefix), StaticPart(this.defaultPrefix), StaticPart("api/students/current")))
  )
  private lazy val controllers_StudentStatsController_getCurrentStudent4_invoker = createInvoker(
    StudentStatsController_1.getCurrentStudent,
    play.api.routing.HandlerDef(this.getClass.getClassLoader,
      "router",
      "controllers.StudentStatsController",
      "getCurrentStudent",
      Nil,
      "GET",
      this.prefix + """api/students/current""",
      """ Student Stats""",
      Seq()
    )
  )

  // @LINE:12
  private lazy val controllers_StudentStatsController_getStudentStats5_route = Route("GET",
    PathPattern(List(StaticPart(this.prefix), StaticPart(this.defaultPrefix), StaticPart("api/students/"), DynamicPart("id", """[^/]+""", encodeable=true), StaticPart("/stats")))
  )
  private lazy val controllers_StudentStatsController_getStudentStats5_invoker = createInvoker(
    StudentStatsController_1.getStudentStats(fakeValue[String]),
    play.api.routing.HandlerDef(this.getClass.getClassLoader,
      "router",
      "controllers.StudentStatsController",
      "getStudentStats",
      Seq(classOf[String]),
      "GET",
      this.prefix + """api/students/""" + "$" + """id<[^/]+>/stats""",
      """""",
      Seq()
    )
  )

  // @LINE:13
  private lazy val controllers_StudentStatsController_getCourseProgress6_route = Route("GET",
    PathPattern(List(StaticPart(this.prefix), StaticPart(this.defaultPrefix), StaticPart("api/students/"), DynamicPart("id", """[^/]+""", encodeable=true), StaticPart("/progress")))
  )
  private lazy val controllers_StudentStatsController_getCourseProgress6_invoker = createInvoker(
    StudentStatsController_1.getCourseProgress(fakeValue[String]),
    play.api.routing.HandlerDef(this.getClass.getClassLoader,
      "router",
      "controllers.StudentStatsController",
      "getCourseProgress",
      Seq(classOf[String]),
      "GET",
      this.prefix + """api/students/""" + "$" + """id<[^/]+>/progress""",
      """""",
      Seq()
    )
  )

  // @LINE:14
  private lazy val controllers_StudentStatsController_getRiskPredictions7_route = Route("GET",
    PathPattern(List(StaticPart(this.prefix), StaticPart(this.defaultPrefix), StaticPart("api/students/"), DynamicPart("id", """[^/]+""", encodeable=true), StaticPart("/risks")))
  )
  private lazy val controllers_StudentStatsController_getRiskPredictions7_invoker = createInvoker(
    StudentStatsController_1.getRiskPredictions(fakeValue[String]),
    play.api.routing.HandlerDef(this.getClass.getClassLoader,
      "router",
      "controllers.StudentStatsController",
      "getRiskPredictions",
      Seq(classOf[String]),
      "GET",
      this.prefix + """api/students/""" + "$" + """id<[^/]+>/risks""",
      """""",
      Seq()
    )
  )

  // @LINE:17
  private lazy val controllers_HealthController_health8_route = Route("GET",
    PathPattern(List(StaticPart(this.prefix), StaticPart(this.defaultPrefix), StaticPart("health")))
  )
  private lazy val controllers_HealthController_health8_invoker = createInvoker(
    HealthController_2.health,
    play.api.routing.HandlerDef(this.getClass.getClassLoader,
      "router",
      "controllers.HealthController",
      "health",
      Nil,
      "GET",
      this.prefix + """health""",
      """ Health Check""",
      Seq()
    )
  )

  // @LINE:20
  private lazy val controllers_Assets_versioned9_route = Route("GET",
    PathPattern(List(StaticPart(this.prefix), StaticPart(this.defaultPrefix), StaticPart("assets/"), DynamicPart("file", """.+""", encodeable=false)))
  )
  private lazy val controllers_Assets_versioned9_invoker = createInvoker(
    Assets_3.versioned(fakeValue[String], fakeValue[Asset]),
    play.api.routing.HandlerDef(this.getClass.getClassLoader,
      "router",
      "controllers.Assets",
      "versioned",
      Seq(classOf[String], classOf[Asset]),
      "GET",
      this.prefix + """assets/""" + "$" + """file<.+>""",
      """ Map static resources from the /public folder to the /assets URL path""",
      Seq()
    )
  )


  def routes: PartialFunction[RequestHeader, Handler] = {
  
    // @LINE:5
    case controllers_AuthController_login0_route(params@_) =>
      call { 
        controllers_AuthController_login0_invoker.call(AuthController_0.login)
      }
  
    // @LINE:6
    case controllers_AuthController_logout1_route(params@_) =>
      call { 
        controllers_AuthController_logout1_invoker.call(AuthController_0.logout)
      }
  
    // @LINE:7
    case controllers_AuthController_register2_route(params@_) =>
      call { 
        controllers_AuthController_register2_invoker.call(AuthController_0.register)
      }
  
    // @LINE:8
    case controllers_AuthController_verifyToken3_route(params@_) =>
      call { 
        controllers_AuthController_verifyToken3_invoker.call(AuthController_0.verifyToken)
      }
  
    // @LINE:11
    case controllers_StudentStatsController_getCurrentStudent4_route(params@_) =>
      call { 
        controllers_StudentStatsController_getCurrentStudent4_invoker.call(StudentStatsController_1.getCurrentStudent)
      }
  
    // @LINE:12
    case controllers_StudentStatsController_getStudentStats5_route(params@_) =>
      call(params.fromPath[String]("id", None)) { (id) =>
        controllers_StudentStatsController_getStudentStats5_invoker.call(StudentStatsController_1.getStudentStats(id))
      }
  
    // @LINE:13
    case controllers_StudentStatsController_getCourseProgress6_route(params@_) =>
      call(params.fromPath[String]("id", None)) { (id) =>
        controllers_StudentStatsController_getCourseProgress6_invoker.call(StudentStatsController_1.getCourseProgress(id))
      }
  
    // @LINE:14
    case controllers_StudentStatsController_getRiskPredictions7_route(params@_) =>
      call(params.fromPath[String]("id", None)) { (id) =>
        controllers_StudentStatsController_getRiskPredictions7_invoker.call(StudentStatsController_1.getRiskPredictions(id))
      }
  
    // @LINE:17
    case controllers_HealthController_health8_route(params@_) =>
      call { 
        controllers_HealthController_health8_invoker.call(HealthController_2.health)
      }
  
    // @LINE:20
    case controllers_Assets_versioned9_route(params@_) =>
      call(Param[String]("path", Right("/public")), params.fromPath[Asset]("file", None)) { (path, file) =>
        controllers_Assets_versioned9_invoker.call(Assets_3.versioned(path, file))
      }
  }
}
