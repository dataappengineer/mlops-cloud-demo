# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = var.tags
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "model_api" {
  name              = "/ecs/${var.project_name}-${var.environment}-model-api"
  retention_in_days = 7  # Free Tier: 5GB storage, 7 days retention

  tags = var.tags
}

# ECS Task Definition
resource "aws_ecs_task_definition" "model_api" {
  family                   = "${var.project_name}-${var.environment}-model-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.model_api_cpu
  memory                   = var.model_api_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name  = "model-api"
    image = "${aws_ecr_repository.model_api.repository_url}:latest"
    
    portMappings = [{
      containerPort = var.model_api_container_port
      protocol      = "tcp"
    }]

    environment = [
      {
        name  = "AWS_DEFAULT_REGION"
        value = var.aws_region
      },
      {
        name  = "S3_BUCKET_NAME"
        value = var.s3_bucket_name
      },
      {
        name  = "MODEL_KEY"
        value = "model.joblib"
      },
      {
        name  = "LOG_LEVEL"
        value = "INFO"
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.model_api.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:${var.model_api_container_port}/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])

  tags = var.tags
}

# ECS Service
resource "aws_ecs_service" "model_api" {
  name            = "${var.project_name}-${var.environment}-model-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.model_api.arn
  desired_count   = var.model_api_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = !var.enable_nat_gateway  # Assign public IP if no NAT
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.model_api.arn
    container_name   = "model-api"
    container_port   = var.model_api_container_port
  }

  depends_on = [aws_lb_listener.http]

  tags = var.tags
}