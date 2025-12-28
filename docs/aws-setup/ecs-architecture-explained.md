# Understanding AWS ECS Architecture for MLOps

**Goal**: Deploy your FastAPI model serving API to AWS cloud so anyone can access it via the internet.

## 🎯 The Big Picture

Right now, your API runs on your laptop:
- ✅ Works locally: `http://localhost:8000`
- ❌ Not accessible to others
- ❌ Stops when you close laptop
- ❌ Can't handle multiple users

**We want**:
- ✅ API accessible via internet URL: `http://your-app.aws.com`
- ✅ Runs 24/7 on AWS servers
- ✅ Handles multiple users automatically
- ✅ Costs little to nothing (AWS Free Tier)

## 🏗️ Architecture Components Explained

### The Journey of a Request

When someone wants to use your ML model, here's what happens:

```
User Browser/App
      ↓ (1) Makes HTTP request
Internet (Public Web)
      ↓ (2) Request reaches AWS
Application Load Balancer (ALB)
      ↓ (3) Routes to healthy container
ECS Fargate Container (Your FastAPI App)
      ↓ (4) Loads model from S3
S3 Bucket (model.joblib)
      ↓ (5) Returns prediction
      ↑ (6) Response flows back to user
```

Let me explain each piece:

---

## 1️⃣ **Internet** (The Public Web)

**What it is**: The global network connecting all computers.

**What it does**: Carries requests from users to your AWS infrastructure.

**Analogy**: Like the postal system - anyone can send a letter to your address.

---

## 2️⃣ **Application Load Balancer (ALB)**

**What it is**: AWS service that acts as the "front door" to your application.

**What it does**:
- Gives you a public URL (like `http://mlops-demo-alb-123456.us-east-1.elb.amazonaws.com`)
- Receives all incoming requests from the internet
- Checks if your containers are healthy
- Routes traffic to healthy containers
- Handles many users at once

**Analogy**: Like a receptionist at a hotel:
- Has a public address people can find
- Directs visitors to available rooms
- Checks which rooms are ready
- Handles multiple guests simultaneously

**Why we need it**:
- Your containers can crash/restart - ALB detects this and routes around failures
- Multiple containers can run - ALB distributes traffic between them
- Provides a stable public endpoint even as containers change

**File**: `infrastructure/terraform/alb.tf`

---

## 3️⃣ **ECS (Elastic Container Service)**

**What it is**: AWS service that runs Docker containers.

**What it does**:
- Manages your Docker containers
- Starts/stops/restarts them automatically
- Ensures desired number are always running
- Monitors container health
- Handles deployments when you update code

**Analogy**: Like a building superintendent:
- Makes sure apartments (containers) are running
- Replaces broken units
- Keeps the right number of units available
- Does maintenance and upgrades

**File**: `infrastructure/terraform/ecs.tf`

---

## 4️⃣ **Fargate** (ECS Launch Type)

**What it is**: "Serverless" mode for ECS - AWS manages the servers for you.

**What it does**:
- You don't need to manage EC2 instances
- AWS automatically provisions the right amount of compute
- You only pay for what you use (by the second)
- No server patching or maintenance

**Traditional vs Fargate**:
```
Traditional (EC2):
You → Manage Servers → Run Containers → Run App

Fargate:
You → Run Containers → Run App
     ↑
AWS manages servers automatically
```

**Why we use it**:
- Simpler - no server management
- Cheaper for small workloads (Free Tier eligible)
- Auto-scales automatically
- Perfect for learning and demos

**Configured in**: `infrastructure/terraform/ecs.tf` (line: `launch_type = "FARGATE"`)

---

## 5️⃣ **Container (Docker)**

**What it is**: Your FastAPI app packaged with all its dependencies.

**What it does**:
- Runs your Python code
- Includes FastAPI, scikit-learn, all libraries
- Always works the same way everywhere
- Isolated from other containers

**Analogy**: Like a food truck:
- Self-contained kitchen (your app + dependencies)
- Can park anywhere (runs on any computer)
- Same menu everywhere (consistent behavior)

**Your container**:
- Built from: `model-api/Dockerfile`
- Contains: Python 3.9, FastAPI, scikit-learn, your code
- Exposes: Port 8000 for HTTP requests

---

## 6️⃣ **ECR (Elastic Container Registry)**

**What it is**: AWS's Docker Hub - stores your Docker images.

**What it does**:
- Stores your container images
- Scans for security vulnerabilities
- Manages image versions (tags)
- ECS pulls images from here

**Analogy**: Like GitHub, but for Docker images instead of code.

**Workflow**:
```
1. Build image on your laptop: docker build
2. Push to ECR: docker push
3. ECS pulls from ECR: docker pull
4. ECS runs the container
```

**File**: `infrastructure/terraform/ecr.tf`

---

## 7️⃣ **S3 (Simple Storage Service)**

**What it is**: AWS's file storage service.

**What it does**:
- Stores your trained model (`model.joblib`)
- Your container downloads model at startup
- Cheap storage (~$0.023 per GB/month)
- Highly available and durable

**Why not put model in container?**
- ❌ Container images should be small
- ❌ Rebuilding container for each model update is slow
- ✅ S3 allows model updates without rebuilding image
- ✅ Multiple containers can share same model

**Your setup**:
- Bucket: `mlops-processed-data-982248023588`
- Model: `model.joblib`
- Container downloads at startup

---

## 🔐 Supporting Components

### **VPC (Virtual Private Cloud)**

**What it is**: Your private network in AWS.

**What it does**:
- Isolates your resources from others
- Controls traffic flow with subnets and routing
- Like having your own building in AWS's data center

**Structure**:
```
VPC (10.0.0.0/16)
├── Public Subnets (10.0.0.0/24, 10.0.1.0/24)
│   └── Application Load Balancer lives here
│   └── Has internet access
└── Private Subnets (10.0.10.0/24, 10.0.11.0/24)
    └── Your containers live here
    └── Protected from direct internet access
```

**File**: `infrastructure/terraform/vpc.tf`

---

### **Security Groups**

**What it is**: Virtual firewalls for your resources.

**What it does**:
- Controls what traffic is allowed in/out
- Protects your containers from unauthorized access

**Our security groups**:

**ALB Security Group**:
- ✅ Allow: Port 80 (HTTP) from anywhere on the internet
- ✅ Allow: All outbound traffic
- Purpose: Let users access your API

**ECS Security Group**:
- ✅ Allow: Port 8000 from ALB only
- ✅ Allow: All outbound (for S3, CloudWatch)
- Purpose: Only ALB can reach containers

**File**: `infrastructure/terraform/security_groups.tf`

---

### **IAM (Identity and Access Management)**

**What it is**: AWS's permission system.

**What it does**:
- Controls what your containers can access
- Follows "least privilege" principle

**Our IAM roles**:

**ECS Execution Role**:
- Used by ECS to start your container
- Permissions: Pull images from ECR, write CloudWatch logs

**ECS Task Role**:
- Used by your application code
- Permissions: Read from S3 bucket (get model.joblib)

**File**: `infrastructure/terraform/iam.tf`

---

### **CloudWatch Logs**

**What it is**: AWS's logging service.

**What it does**:
- Collects logs from your containers
- Searchable and viewable in AWS Console
- Helps debug issues

**What gets logged**:
- Your FastAPI startup messages
- Request logs
- Errors and exceptions
- Model loading status

**How to view**:
```bash
aws logs tail /ecs/mlops-demo-dev-model-api --follow
```

---

## 🔄 Complete Request Flow

Let's trace what happens when someone makes a prediction request:

### **Step 1: User Makes Request**
```bash
curl http://your-alb-url.amazonaws.com/predict -d '{"features": {...}}'
```

### **Step 2: DNS Routes to ALB**
- Request goes to internet
- AWS directs to your ALB's public IP

### **Step 3: ALB Receives Request**
- ALB checks: "Which containers are healthy?"
- Finds healthy container at 10.0.10.15:8000
- Forwards request there

### **Step 4: Container Processes Request**
- FastAPI receives POST to `/predict`
- Checks if model loaded (from S3)
- Runs prediction with scikit-learn
- Returns JSON response

### **Step 5: Response Returns**
```json
{
  "prediction": 5,
  "confidence": 0.98,
  "processing_time_ms": 10.35
}
```

### **Step 6: ALB Sends to User**
- ALB forwards response back through internet
- User receives prediction

**All in ~100ms!**

---

## 💰 Cost Breakdown (Free Tier)

| Service | Free Tier | Our Usage | Cost |
|---------|-----------|-----------|------|
| ECS Fargate | 750 hours/month | 720 hours (1 container) | $0 |
| ALB | 750 hours + 15GB | ~730 hours + minimal data | $0 |
| ECR | 500MB storage | ~200MB (1 image) | $0 |
| S3 | 5GB storage | 0.003GB (model) | $0 |
| CloudWatch | 5GB logs | <1GB logs | $0 |
| NAT Gateway | ⚠️ NOT FREE | **DISABLED** | $0 |

**Monthly Cost**: $0 (within Free Tier limits)

---

## 🎓 Learning Checklist

Before deploying, make sure you understand:

- [ ] What each component does (review above)
- [ ] Why we need ALB (traffic routing, health checks)
- [ ] What Fargate does (runs containers without managing servers)
- [ ] How your code gets to AWS (Docker → ECR → ECS)
- [ ] Where the model lives (S3) and how container accesses it (IAM)
- [ ] How to view logs (CloudWatch)
- [ ] How much it costs (Free Tier breakdown)

---

## 📚 Recommended Learning Path

### **1. Understanding Docker** (if needed)
- What containers are
- Dockerfile basics
- Building and running images
- Try: `docker run hello-world`

### **2. Understanding Basic AWS**
- What regions and availability zones are
- Basic networking (VPC, subnets)
- IAM roles vs policies
- S3 basics

### **3. Understanding ECS**
- Task definitions (container specs)
- Services (manages running tasks)
- Fargate vs EC2 launch types
- How ECS pulls from ECR

### **4. Hands-On Testing**
Once you understand the components, we can:
1. Deploy with Terraform
2. Monitor in AWS Console
3. Test the API
4. View logs
5. Update the service

---

## 🤔 Common Questions

**Q: Why not just run this on my laptop?**
A: Your laptop isn't accessible from the internet, turns off at night, and can't handle many users.

**Q: Why so many components? Can't we simplify?**
A: Each component has a specific job:
- ALB = public endpoint + health checks
- ECS = manages containers
- ECR = stores images
- VPC = network security
- IAM = access control

All are needed for production-grade deployment.

**Q: What if my container crashes?**
A: ECS automatically restarts it! ALB detects unhealthy containers and stops sending traffic.

**Q: How do I update my model?**
A: Two ways:
1. Upload new `model.joblib` to S3, restart container
2. Rebuild Docker image, push to ECR, update ECS service

**Q: Can I see the AWS Console?**
A: Yes! Log into AWS Console and you'll see all these resources.

---

## 🎯 Next Steps

**Option 1: Learn More First**
- Read AWS ECS documentation
- Watch: "AWS ECS Tutorial for Beginners" on YouTube
- Explore: AWS Console in browser
- Review the Terraform files with new understanding

**Option 2: Deploy and Learn**
- Install Terraform
- Run `terraform plan` to see what will be created
- Deploy to AWS
- Explore resources in AWS Console
- Test your API
- Learn by doing!

**My Recommendation**: Review this document, then we can deploy together while I explain each step in real-time.

---

## 📖 Files Reference

| File | Purpose | What to Look At |
|------|---------|-----------------|
| `vpc.tf` | Network setup | Subnet CIDR blocks, routing |
| `alb.tf` | Load balancer | Listener (port 80), health checks |
| `ecs.tf` | Container service | Task definition, container config |
| `ecr.tf` | Image storage | Repository name |
| `iam.tf` | Permissions | S3 access policy |
| `security_groups.tf` | Firewalls | Allowed ports |
| `variables.tf` | Configuration | CPU/memory settings |
| `outputs.tf` | Important values | ALB URL, ECR repo |

Ready to take the next step? Do you want to:
1. Review any specific component in detail?
2. Walk through the Terraform files together?
3. Deploy and learn by exploring AWS Console?
