name := "student-risk-prediction"
version := "1.0.0"
scalaVersion := "2.13.16"

lazy val root = (project in file("."))
  .enablePlugins(PlayScala)
  .settings(
    libraryDependencies ++= Seq(
      guice,
      "com.datastax.oss" % "java-driver-core" % "4.17.0",
      "com.datastax.oss" % "java-driver-query-builder" % "4.17.0",
      "com.auth0" % "java-jwt" % "4.4.0",
      "org.mindrot" % "jbcrypt" % "0.4",
      "com.typesafe.play" %% "play-json" % "2.10.4",
      "org.scalatestplus.play" %% "scalatestplus-play" % "7.0.1" % Test
    )
  )

resolvers += "Akka library repository".at("https://repo.akka.io/maven")