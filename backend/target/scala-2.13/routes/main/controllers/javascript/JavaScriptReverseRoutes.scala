// @GENERATOR:play-routes-compiler
// @SOURCE:conf/routes

import play.api.routing.JavaScriptReverseRoute


import _root_.controllers.Assets.Asset

// @LINE:5
package controllers.javascript {

  // @LINE:5
  class ReverseAuthController(_prefix: => String) {

    def _defaultPrefix: String = {
      if (_prefix.endsWith("/")) "" else "/"
    }

  
    // @LINE:5
    def login: JavaScriptReverseRoute = JavaScriptReverseRoute(
      "controllers.AuthController.login",
      """
        function() {
          return _wA({method:"POST", url:"""" + _prefix + { _defaultPrefix } + """" + "auth/login"})
        }
      """
    )
  
    // @LINE:6
    def logout: JavaScriptReverseRoute = JavaScriptReverseRoute(
      "controllers.AuthController.logout",
      """
        function() {
          return _wA({method:"POST", url:"""" + _prefix + { _defaultPrefix } + """" + "auth/logout"})
        }
      """
    )
  
    // @LINE:7
    def register: JavaScriptReverseRoute = JavaScriptReverseRoute(
      "controllers.AuthController.register",
      """
        function() {
          return _wA({method:"POST", url:"""" + _prefix + { _defaultPrefix } + """" + "auth/register"})
        }
      """
    )
  
    // @LINE:8
    def verifyToken: JavaScriptReverseRoute = JavaScriptReverseRoute(
      "controllers.AuthController.verifyToken",
      """
        function() {
          return _wA({method:"GET", url:"""" + _prefix + { _defaultPrefix } + """" + "auth/verify"})
        }
      """
    )
  
  }

  // @LINE:11
  class ReverseStudentStatsController(_prefix: => String) {

    def _defaultPrefix: String = {
      if (_prefix.endsWith("/")) "" else "/"
    }

  
    // @LINE:11
    def getCurrentStudent: JavaScriptReverseRoute = JavaScriptReverseRoute(
      "controllers.StudentStatsController.getCurrentStudent",
      """
        function() {
          return _wA({method:"GET", url:"""" + _prefix + { _defaultPrefix } + """" + "api/students/current"})
        }
      """
    )
  
    // @LINE:12
    def getStudentStats: JavaScriptReverseRoute = JavaScriptReverseRoute(
      "controllers.StudentStatsController.getStudentStats",
      """
        function(id0) {
          return _wA({method:"GET", url:"""" + _prefix + { _defaultPrefix } + """" + "api/students/" + encodeURIComponent((""" + implicitly[play.api.mvc.PathBindable[String]].javascriptUnbind + """)("id", id0)) + "/stats"})
        }
      """
    )
  
    // @LINE:13
    def getCourseProgress: JavaScriptReverseRoute = JavaScriptReverseRoute(
      "controllers.StudentStatsController.getCourseProgress",
      """
        function(id0) {
          return _wA({method:"GET", url:"""" + _prefix + { _defaultPrefix } + """" + "api/students/" + encodeURIComponent((""" + implicitly[play.api.mvc.PathBindable[String]].javascriptUnbind + """)("id", id0)) + "/progress"})
        }
      """
    )
  
    // @LINE:14
    def getRiskPredictions: JavaScriptReverseRoute = JavaScriptReverseRoute(
      "controllers.StudentStatsController.getRiskPredictions",
      """
        function(id0) {
          return _wA({method:"GET", url:"""" + _prefix + { _defaultPrefix } + """" + "api/students/" + encodeURIComponent((""" + implicitly[play.api.mvc.PathBindable[String]].javascriptUnbind + """)("id", id0)) + "/risks"})
        }
      """
    )
  
  }

  // @LINE:17
  class ReverseHealthController(_prefix: => String) {

    def _defaultPrefix: String = {
      if (_prefix.endsWith("/")) "" else "/"
    }

  
    // @LINE:17
    def health: JavaScriptReverseRoute = JavaScriptReverseRoute(
      "controllers.HealthController.health",
      """
        function() {
          return _wA({method:"GET", url:"""" + _prefix + { _defaultPrefix } + """" + "health"})
        }
      """
    )
  
  }

  // @LINE:20
  class ReverseAssets(_prefix: => String) {

    def _defaultPrefix: String = {
      if (_prefix.endsWith("/")) "" else "/"
    }

  
    // @LINE:20
    def versioned: JavaScriptReverseRoute = JavaScriptReverseRoute(
      "controllers.Assets.versioned",
      """
        function(file1) {
          return _wA({method:"GET", url:"""" + _prefix + { _defaultPrefix } + """" + "assets/" + (""" + implicitly[play.api.mvc.PathBindable[Asset]].javascriptUnbind + """)("file", file1)})
        }
      """
    )
  
  }


}
