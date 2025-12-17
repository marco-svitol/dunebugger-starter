#!/bin/bash
# Dunebugger Starter Service Management Script

SERVICE_NAME="dunebugger-starter"
APP_DIR="/opt/dunebugger-starter"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_usage() {
    echo "Usage: $0 {start|stop|restart|status|enable|disable|logs|config|install|uninstall}"
    echo ""
    echo "Commands:"
    echo "  start      - Start the service"
    echo "  stop       - Stop the service"
    echo "  restart    - Restart the service"
    echo "  status     - Show service status"
    echo "  enable     - Enable service to start at boot"
    echo "  disable    - Disable service from starting at boot"
    echo "  logs       - Show service logs (follow mode)"
    echo "  config     - Edit configuration file"
    echo "  install    - Run installation script"
    echo "  uninstall  - Remove service and files"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}This command requires root privileges. Use sudo.${NC}"
        exit 1
    fi
}

case "$1" in
    start)
        check_root
        echo -e "${BLUE}Starting $SERVICE_NAME...${NC}"
        systemctl start $SERVICE_NAME
        systemctl status $SERVICE_NAME --no-pager -l
        ;;
    stop)
        check_root
        echo -e "${BLUE}Stopping $SERVICE_NAME...${NC}"
        systemctl stop $SERVICE_NAME
        echo -e "${GREEN}Service stopped.${NC}"
        ;;
    restart)
        check_root
        echo -e "${BLUE}Restarting $SERVICE_NAME...${NC}"
        systemctl restart $SERVICE_NAME
        systemctl status $SERVICE_NAME --no-pager -l
        ;;
    status)
        systemctl status $SERVICE_NAME --no-pager -l
        ;;
    enable)
        check_root
        echo -e "${BLUE}Enabling $SERVICE_NAME to start at boot...${NC}"
        systemctl enable $SERVICE_NAME
        echo -e "${GREEN}Service enabled.${NC}"
        ;;
    disable)
        check_root
        echo -e "${BLUE}Disabling $SERVICE_NAME from starting at boot...${NC}"
        systemctl disable $SERVICE_NAME
        echo -e "${YELLOW}Service disabled.${NC}"
        ;;
    logs)
        echo -e "${BLUE}Showing logs for $SERVICE_NAME (Ctrl+C to exit)...${NC}"
        journalctl -u $SERVICE_NAME -f
        ;;
    config)
        if [ -f "$APP_DIR/app/config/dunebugger-starter.conf" ]; then
            echo -e "${BLUE}Opening configuration file...${NC}"
            ${EDITOR:-nano} "$APP_DIR/app/config/dunebugger-starter.conf"
            echo -e "${YELLOW}Configuration updated. Restart the service to apply changes:${NC}"
            echo "  sudo $0 restart"
        else
            echo -e "${RED}Configuration file not found: $APP_DIR/app/config/dunebugger-starter.conf${NC}"
            exit 1
        fi
        ;;
    install)
        check_root
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        if [ -f "$SCRIPT_DIR/install.sh" ]; then
            bash "$SCRIPT_DIR/install.sh"
        else
            echo -e "${RED}Installation script not found: $SCRIPT_DIR/install.sh${NC}"
            exit 1
        fi
        ;;
    uninstall)
        check_root
        echo -e "${YELLOW}This will remove the service and all files. Are you sure? (y/N)${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo -e "${BLUE}Stopping and disabling service...${NC}"
            systemctl stop $SERVICE_NAME 2>/dev/null || true
            systemctl disable $SERVICE_NAME 2>/dev/null || true
            
            echo -e "${BLUE}Removing service file...${NC}"
            rm -f /etc/systemd/system/${SERVICE_NAME}.service
            
            echo -e "${BLUE}Removing application directory...${NC}"
            rm -rf "$APP_DIR"
            
            echo -e "${BLUE}Reloading systemd...${NC}"
            systemctl daemon-reload
            
            echo -e "${GREEN}Uninstallation completed.${NC}"
        else
            echo -e "${YELLOW}Uninstallation cancelled.${NC}"
        fi
        ;;
    *)
        print_usage
        exit 1
        ;;
esac