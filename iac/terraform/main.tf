resource "kubernetes_pod" "Sample" {
  metadata {
    name = "Sample"
    namespace = "evolved5g"
    labels = {
      app = "SampleApp"
    }
  }

  spec {
    container {
      image = "dockerhub.hi.inet/evolved-5g/Sample:latest"
      name  = "SampleContainer"
    }
  }
}

resource "kubernetes_service" "Sample_service" {
  metadata {
    name = "SampleService"
    namespace = "evolved5g"
  }
  spec {
    selector = {
      app = Add the NetApp service app
    }
    port {
      port = 1191
      target_port = 1191
    }
  }
}
