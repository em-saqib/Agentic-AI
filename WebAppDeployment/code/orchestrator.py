"""
Orchestrator - Coordinates WordPress deployment
"""
import os
import subprocess
import time
from mysql_agent import MySQLAgent
from webserver_agent import WebServerAgent


class Orchestrator:
    def __init__(self, config):
        self.config = config

        # Create specialized agents
        self.mysql_agent = MySQLAgent(config)
        self.webserver_agent = WebServerAgent(config)

    def create_docker_compose(self):
        """Create docker-compose.yml file"""
        mysql_config = self.config['mysql']
        wordpress_config = self.config['wordpress']

        compose_content = f"""version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: wp-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: {mysql_config['root_password']}
      MYSQL_DATABASE: {mysql_config['database']}
      MYSQL_USER: {mysql_config['user']}
      MYSQL_PASSWORD: {mysql_config['password']}
    volumes:
      - mysql_data:/var/lib/mysql

  wordpress:
    image: wordpress:latest
    container_name: wp-wordpress
    restart: always
    ports:
      - "{wordpress_config['port']}:80"
    environment:
      WORDPRESS_DB_HOST: mysql:3306
      WORDPRESS_DB_NAME: {mysql_config['database']}
      WORDPRESS_DB_USER: {mysql_config['user']}
      WORDPRESS_DB_PASSWORD: {mysql_config['password']}
    volumes:
      - wordpress_data:/var/www/html
    depends_on:
      - mysql

volumes:
  mysql_data:
  wordpress_data:
"""

        with open('docker-compose.yml', 'w') as f:
            f.write(compose_content)

        print("✓ Created docker-compose.yml")

# Incorporate LLM: 
# 1. Dynamic docker-compose generation (generate a docker-compose.yml for WordPress and MySQL with these parameters)
# 2. Query the LLM to compare current config with desired state, propose updates, and optionally return the modified YAML.
# 3. Use LLM to plan the sequence of deployment tasks dynamically based on service dependencies, resource availability, or custom user requirements.
# 4. Feed the error to the LLM and get step-by-step recovery instructions
# Challenges: Relaibility of output, multi-step reasoning and state management, large output, latency, 

    def start_containers(self):
        """Start Docker containers"""
        print("\n=== Starting Docker Containers ===")

        result = subprocess.run(
            "docker-compose up -d",
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✓ Containers started")
            return True
        else:
            print(f"✗ Failed to start containers: {result.stderr}")
            return False

    def deploy(self):
        """Main deployment workflow"""
        print("\n" + "="*60)
        print("WORDPRESS DEPLOYMENT - Multi-Agent System")
        print("="*60)

        # Step 1: Create docker-compose file
        print("\n[Step 1] Creating configuration...")
        self.create_docker_compose()

        # if os.path.exists("docker-compose.yml"):
        #     mysql_config = self.config['mysql']
        #     wordpress_config = self.config['wordpress']
        #     compose_content = f"""version: '3.8'
        # else
        #     self.create_docker_compose()

        # Step 2: Start containers
        print("\n[Step 2] Starting containers...")
        if not self.start_containers():
            return {"status": "failed", "message": "Could not start containers"}

        # Step 3: Wait for services to initialize
        print("\n[Step 3] Waiting few seconds for services to initialize...")
        time.sleep(10)

        # Step 4: Validate MySQL with agent
        print("\n[Step 4] Validating MySQL...")
        mysql_result = self.mysql_agent.validate(
            container_name='wp-mysql',
            user=self.config['mysql']['user'],
            password=self.config['mysql']['password'],
            database=self.config['mysql']['database']
        )

        if mysql_result['status'] != 'success':
            return {
                "status": "failed",
                "message": "MySQL validation failed",
                "details": mysql_result
            }

        # Step 5: Validate WordPress with agent
        print("\n[Step 5] Validating WordPress...")
        wordpress_url = f"http://localhost:{self.config['wordpress']['port']}"

        webserver_result = self.webserver_agent.validate(
            container_name='wp-wordpress',
            wordpress_url=wordpress_url
        )

        if webserver_result['status'] != 'success':
            return {
                "status": "failed",
                "message": "WordPress validation failed",
                "details": webserver_result
            }

        # Success!
        print("\n" + "="*60)
        print("✓ DEPLOYMENT SUCCESSFUL!")
        print("="*60)
        print(f"\nWordPress URL: {wordpress_url}")
        print(f"Admin User: {self.config['wordpress']['admin_user']}")
        print(f"Admin Password: {self.config['wordpress']['admin_password']}")
        print(f"\nComplete setup at: {wordpress_url}/wp-admin/install.php")
        print("="*60 + "\n")

        return {
            "status": "success",
            "wordpress_url": wordpress_url,
            "mysql_status": mysql_result['status'],
            "webserver_status": webserver_result['status']
        }

    def stop(self):
        """Stop containers"""
        print("\n=== Stopping WordPress ===")
        subprocess.run("docker-compose down", shell=True)
        print("✓ Containers stopped\n")
