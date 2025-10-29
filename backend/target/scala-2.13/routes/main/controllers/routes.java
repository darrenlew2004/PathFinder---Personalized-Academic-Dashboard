// @GENERATOR:play-routes-compiler
// @SOURCE:conf/routes

package controllers;

import router.RoutesPrefix;

public class routes {
  
  public static final controllers.ReverseAuthController AuthController = new controllers.ReverseAuthController(RoutesPrefix.byNamePrefix());
  public static final controllers.ReverseStudentStatsController StudentStatsController = new controllers.ReverseStudentStatsController(RoutesPrefix.byNamePrefix());
  public static final controllers.ReverseHealthController HealthController = new controllers.ReverseHealthController(RoutesPrefix.byNamePrefix());
  public static final controllers.ReverseAssets Assets = new controllers.ReverseAssets(RoutesPrefix.byNamePrefix());

  public static class javascript {
    
    public static final controllers.javascript.ReverseAuthController AuthController = new controllers.javascript.ReverseAuthController(RoutesPrefix.byNamePrefix());
    public static final controllers.javascript.ReverseStudentStatsController StudentStatsController = new controllers.javascript.ReverseStudentStatsController(RoutesPrefix.byNamePrefix());
    public static final controllers.javascript.ReverseHealthController HealthController = new controllers.javascript.ReverseHealthController(RoutesPrefix.byNamePrefix());
    public static final controllers.javascript.ReverseAssets Assets = new controllers.javascript.ReverseAssets(RoutesPrefix.byNamePrefix());
  }

}
