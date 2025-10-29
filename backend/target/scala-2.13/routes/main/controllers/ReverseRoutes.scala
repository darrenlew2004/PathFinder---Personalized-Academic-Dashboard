// @GENERATOR:play-routes-compiler
// @SOURCE:conf/routes

import play.api.mvc.Call


import _root_.controllers.Assets.Asset

// @LINE:5
package controllers {

  // @LINE:5
  class ReverseAuthController(_prefix: => String) {
    def _defaultPrefix: String = {
      if (_prefix.endsWith("/")) "" else "/"
    }

  
    // @LINE:5
    def login: Call = {
      
      Call("POST", _prefix + { _defaultPrefix } + "auth/login")
    }
  
    // @LINE:6
    def logout: Call = {
      
      Call("POST", _prefix + { _defaultPrefix } + "auth/logout")
    }
  
    // @LINE:7
    def register: Call = {
      
      Call("POST", _prefix + { _defaultPrefix } + "auth/register")
    }
  
    // @LINE:8
    def verifyToken: Call = {
      
      Call("GET", _prefix + { _defaultPrefix } + "auth/verify")
    }
  
  }

  // @LINE:11
  class ReverseStudentStatsController(_prefix: => String) {
    def _defaultPrefix: String = {
      if (_prefix.endsWith("/")) "" else "/"
    }

  
    // @LINE:11
    def getCurrentStudent: Call = {
      
      Call("GET", _prefix + { _defaultPrefix } + "api/students/current")
    }
  
    // @LINE:12
    def getStudentStats(id:String): Call = {
      
      Call("GET", _prefix + { _defaultPrefix } + "api/students/" + play.core.routing.dynamicString(implicitly[play.api.mvc.PathBindable[String]].unbind("id", id)) + "/stats")
    }
  
    // @LINE:13
    def getCourseProgress(id:String): Call = {
      
      Call("GET", _prefix + { _defaultPrefix } + "api/students/" + play.core.routing.dynamicString(implicitly[play.api.mvc.PathBindable[String]].unbind("id", id)) + "/progress")
    }
  
    // @LINE:14
    def getRiskPredictions(id:String): Call = {
      
      Call("GET", _prefix + { _defaultPrefix } + "api/students/" + play.core.routing.dynamicString(implicitly[play.api.mvc.PathBindable[String]].unbind("id", id)) + "/risks")
    }
  
  }

  // @LINE:17
  class ReverseHealthController(_prefix: => String) {
    def _defaultPrefix: String = {
      if (_prefix.endsWith("/")) "" else "/"
    }

  
    // @LINE:17
    def health: Call = {
      
      Call("GET", _prefix + { _defaultPrefix } + "health")
    }
  
  }

  // @LINE:20
  class ReverseAssets(_prefix: => String) {
    def _defaultPrefix: String = {
      if (_prefix.endsWith("/")) "" else "/"
    }

  
    // @LINE:20
    def versioned(file:Asset): Call = {
      implicit lazy val _rrc = new play.core.routing.ReverseRouteContext(Map(("path", "/public"))); _rrc
      Call("GET", _prefix + { _defaultPrefix } + "assets/" + implicitly[play.api.mvc.PathBindable[Asset]].unbind("file", file))
    }
  
  }


}
