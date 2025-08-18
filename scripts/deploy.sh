#!/bin/bash

# LibriPal Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

# Configuration
PROJECT_NAME="libripal"
DOCKER_REGISTRY=${DOCKER_REGISTRY:-""}
VERSION=${VERSION:-"latest"}
ENVIRONMENT=${ENVIRONMENT:-"production"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️ INFO:${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ SUCCESS:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️ WARNING:${NC} $1"
}

log_error() {
    echo -e "${RED}❌ ERROR:${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_warning "Please edit .env file with your configuration before proceeding"
            exit 1
        else
            log_error ".env.example file not found"
            exit 1
        fi
    fi
    
    log_success "Prerequisites check passed"
}

# Load environment variables
load_environment() {
    log_info "Loading environment variables..."
    
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
        log_success "Environment variables loaded"
    else
        log_error ".env file not found"
        exit 1
    fi
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Build backend image
    log_info "Building backend image..."
    docker build -f docker/Dockerfile.backend -t ${PROJECT_NAME}-backend:${VERSION} .
    
    # Build frontend image
    log_info "Building frontend image..."
    docker build -f docker/Dockerfile.frontend -t ${PROJECT_NAME}-frontend:${VERSION} .
    
    # Build telegram bot image
    log_info "Building telegram bot image..."
    docker build -f docker/Dockerfile.telegram -t ${PROJECT_NAME}-telegram:${VERSION} .
    
    log_success "All images built successfully"
}

# Tag and push images (if registry is specified)
push_images() {
    if [ -n "$DOCKER_REGISTRY" ]; then
        log_info "Pushing images to registry..."
        
        # Tag images
        docker tag ${PROJECT_NAME}-backend:${VERSION} ${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:${VERSION}
        docker tag ${PROJECT_NAME}-frontend:${VERSION} ${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:${VERSION}
        docker tag ${PROJECT_NAME}-telegram:${VERSION} ${DOCKER_REGISTRY}/${PROJECT_NAME}-telegram:${VERSION}
        
        # Push images
        docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:${VERSION}
        docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:${VERSION}
        docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}-telegram:${VERSION}
        
        log_success "Images pushed to registry"
    else
        log_info "No registry specified, skipping image push"
    fi
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Start only the database service
    docker-compose up -d postgres
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 10
    
    # Run setup script
    if command -v python3 &> /dev/null; then
        python3 scripts/setup_database.py setup
    else
        log_warning "Python3 not found locally, running setup in container..."
        docker-compose run --rm backend python scripts/setup_database.py setup
    fi
    
    log_success "Database migrations completed"
}

# Deploy application
deploy_application() {
    log_info "Deploying application..."
    
    # Stop any running containers
    docker-compose down
    
    # Start all services
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Health check
    log_info "Performing health checks..."
    
    # Check backend health
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "Backend is healthy"
    else
        log_error "Backend health check failed"
        exit 1
    fi
    
    # Check frontend
    if curl -f http://localhost:3000/health &> /dev/null; then
        log_success "Frontend is healthy"
    else
        log_warning "Frontend health check failed (this might be normal if it's behind a reverse proxy)"
    fi
    
    log_success "Application deployed successfully"
}

# Backup database
backup_database() {
    log_info "Creating database backup..."
    
    BACKUP_DIR="./backups"
    BACKUP_FILE="${BACKUP_DIR}/libripal_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    mkdir -p $BACKUP_DIR
    
    docker-compose exec postgres pg_dump -U libripal_user libripal > $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        log_success "Database backup created: $BACKUP_FILE"
    else
        log_error "Database backup failed"
        exit 1
    fi
}

# Rollback deployment
rollback_deployment() {
    log_warning "Rolling back deployment..."
    
    # Stop current containers
    docker-compose down
    
    # Restore from backup (if available)
    LATEST_BACKUP=$(ls -t ./backups/*.sql 2>/dev/null | head -1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        log_info "Restoring from backup: $LATEST_BACKUP"
        
        # Start database
        docker-compose up -d postgres
        sleep 10
        
        # Restore backup
        docker-compose exec -T postgres psql -U libripal_user libripal < $LATEST_BACKUP
        
        log_success "Database restored from backup"
    else
        log_warning "No backup found, manual intervention may be required"
    fi
    
    # Start previous version (you would need to implement versioning)
    log_warning "Rollback completed, but you may need to manually deploy the previous version"
}

# Show deployment status
show_status() {
    log_info "Deployment Status:"
    
    echo ""
    docker-compose ps
    
    echo ""
    log_info "Service URLs:"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    
    echo ""
    log_info "Logs can be viewed with:"
    echo "docker-compose logs -f [service_name]"
}

# Cleanup old images and containers
cleanup() {
    log_info "Cleaning up old Docker images and containers..."
    
    # Remove stopped containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (be careful with this)
    docker volume prune -f
    
    log_success "Cleanup completed"
}

# Main deployment function
main_deploy() {
    log_info "Starting LibriPal deployment..."
    
    check_prerequisites
    load_environment
    
    # Create backup before deployment
    if [ "$ENVIRONMENT" = "production" ]; then
        backup_database
    fi
    
    build_images
    push_images
    run_migrations
    deploy_application
    show_status
    
    log_success "Deployment completed successfully! 🎉"
}

# Script usage
usage() {
    echo "Usage: $0 {deploy|rollback|status|backup|cleanup|build}"
    echo ""
    echo "Commands:"
    echo "  deploy   - Full deployment process"
    echo "  rollback - Rollback to previous version"
    echo "  status   - Show deployment status"
    echo "  backup   - Create database backup"
    echo "  cleanup  - Clean up Docker resources"
    echo "  build    - Build Docker images only"
    echo ""
    echo "Environment variables:"
    echo "  ENVIRONMENT - Deployment environment (default: production)"
    echo "  VERSION     - Image version tag (default: latest)"
    echo "  DOCKER_REGISTRY - Docker registry URL (optional)"
    exit 1
}

# Handle command line arguments
case "${1:-}" in
    deploy)
        main_deploy
        ;;
    rollback)
        rollback_deployment
        ;;
    status)
        show_status
        ;;
    backup)
        backup_database
        ;;
    cleanup)
        cleanup
        ;;
    build)
        check_prerequisites
        build_images
        ;;
    *)
        usage
        ;;
esac