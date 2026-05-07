# Krishi Saarthi - Demonstration Suite

This folder contains everything needed to demonstrate Krishi Saarthi to industry stakeholders, investors, and potential partners. The demo is completely isolated from the main project and can be run independently.

## 🎯 Demo Objectives

- **Showcase Voice-First Interface**: Demonstrate Hindi voice interaction for rural users
- **Business Value**: Highlight agricultural commerce capabilities
- **Technical Excellence**: Show production-ready architecture
- **Scalability**: Demonstrate multi-user concurrent operations
- **Real-World Use Cases**: Vendor and consumer workflows

## 📁 Demo Structure

```
demo/
├── README.md                    # This file
├── DEMO_GUIDE.md              # Step-by-step demonstration guide
├── setup/                      # Demo environment setup
│   ├── docker-compose.demo.yml  # Demo-specific Docker setup
│   ├── .env.demo              # Demo environment variables
│   └── init_demo_data.py      # Initialize demo data
├── data/                       # Sample data for demo
│   ├── vendors.json           # Sample vendor profiles
│   ├── consumers.json        # Sample consumer profiles
│   ├── products.json         # Sample product catalog
│   └── conversations.json   # Sample conversation flows
├── scripts/                    # Automation scripts
│   ├── demo_runner.py        # Main demo automation script
│   ├── voice_simulator.py    # Simulate voice inputs
│   ├── data_seeder.py       # Seed demo database
│   └── health_check.py      # Verify demo environment
├── scenarios/                  # Demo scenarios
│   ├── vendor_demo.py       # Vendor workflow demo
│   ├── consumer_demo.py     # Consumer workflow demo
│   ├── udhar_demo.py       # Credit system demo
│   └── multi_user_demo.py  # Multi-user concurrent demo
├── presentation/               # Presentation materials
│   ├── slides.md            # Demo slides content
│   ├── talking_points.md    # Key talking points
│   └── demo_script.md      # Demo narration script
├── monitoring/                 # Demo monitoring
│   ├── dashboard.html       # Live demo dashboard
│   └── metrics.js         # Real-time metrics display
└── assets/                     # Demo assets
    ├── audio_samples/       # Sample audio files
    ├── screenshots/        # Demo screenshots
    └── videos/            # Demo videos
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Node.js 18+ (for frontend)
- Ollama (for local LLM)

### 1. Clone and Setup
```bash
# Clone the main project
git clone <krishi-sarthi-repo>
cd krishi-sarthi

# Navigate to demo folder
cd demo

# Copy demo environment file
cp setup/.env.demo .env
```

### 2. Start Demo Environment
```bash
# Start all services
docker-compose -f setup/docker-compose.demo.yml up -d

# Wait for services to be ready (2-3 minutes)
./scripts/health_check.py
```

### 3. Initialize Demo Data
```bash
# Seed demo database with sample data
python setup/init_demo_data.py

# Verify data was loaded correctly
python scripts/data_seeder.py --verify
```

### 4. Run Demo
```bash
# Start interactive demo
python scripts/demo_runner.py

# Or run specific scenarios
python scenarios/vendor_demo.py
python scenarios/consumer_demo.py
```

## 🎮 Demo Scenarios

### 1. Vendor Workflow Demo
- **Registration**: New vendor onboarding
- **Product Listing**: Voice-based product addition
- **Inventory Management**: Update prices and quantities
- **Order Management**: View and process orders
- **Credit System**: Create and manage udhar

### 2. Consumer Workflow Demo
- **Registration**: New consumer onboarding
- **Product Search**: Voice-based product discovery
- **Order Placement**: Multi-step ordering process
- **Order History**: View past orders
- **Credit Management**: View and pay udhar

### 3. Multi-User Demo
- **Concurrent Operations**: Multiple users simultaneously
- **Real-time Updates**: Live order processing
- **Performance Metrics**: System under load
- **Scalability**: Handle multiple vendors/consumers

### 4. Advanced Features Demo
- **Voice Recognition**: Hindi speech-to-text
- **Natural Language**: LLM-powered conversation
- **Location Services**: Distance-based product discovery
- **Analytics**: Business insights and metrics

## 📊 Demo Metrics

During the demo, the following metrics are displayed:
- **Active Users**: Real-time user count
- **Voice Processing**: STT/TTS performance
- **LLM Response Times**: AI model performance
- **Database Operations**: Query performance
- **Business Metrics**: Orders, revenue, users

## 🎯 Target Audience

### For Investors
- **Market Opportunity**: Rural agricultural commerce
- **Technology Stack**: Modern AI/ML capabilities
- **Scalability**: Multi-region deployment ready
- **Revenue Model**: Multiple monetization streams

### For Industry Partners
- **Integration APIs**: Easy system integration
- **Customization**: White-label solutions
- **Data Analytics**: Business intelligence
- **Support**: Enterprise-grade support

### For Government/NGOs
- **Digital Inclusion**: Rural empowerment
- **Agricultural Impact**: Farmer income improvement
- **Transparency**: Supply chain visibility
- **Compliance**: Regulatory requirements

## 🔧 Customization

### Branding
```bash
# Update demo branding
sed -i 's/Krishi Saarthi/Your Brand Name/g' presentation/slides.md
```

### Data Customization
```bash
# Add your own demo data
cp data/vendors.json data/vendors_custom.json
# Edit the file with your vendor profiles
python scripts/data_seeder.py --custom
```

### Scenario Customization
```bash
# Create custom demo scenarios
cp scenarios/vendor_demo.py scenarios/custom_demo.py
# Modify the script for your specific use case
```

## 📱 Mobile Demo

### Android App
- **APK File**: `assets/mobile/krishi-sarthi-demo.apk`
- **Installation**: Scan QR code or download from link
- **Features**: Full mobile experience with voice

### iOS App
- **TestFlight**: Available via TestFlight invitation
- **Features**: Native iOS experience
- **Installation**: Email invitation required

## 🎥 Video Demo

### Pre-recorded Demo
- **Length**: 5 minutes
- **Content**: Complete feature walkthrough
- **Format**: 1080p MP4
- **Location**: `assets/videos/demo.mp4`

### Live Demo Recording
```bash
# Record live demo session
python scripts/record_demo.py --duration 300 --output demo_recording.mp4
```

## 📞 Support During Demo

### Technical Support
- **Slack Channel**: #demo-support
- **Phone**: +91-XXXX-XXXX-XXXX
- **Email**: demo@krishi-sarthi.com

### Backup Plans
- **Offline Mode**: Pre-recorded demo video
- **Manual Demo**: Step-by-step screenshots
- **Fallback Server**: Alternative demo environment

## 📈 Success Metrics

### Demo Success Indicators
- **Engagement**: Time spent interacting with demo
- **Questions**: Quality and relevance of questions
- **Interest**: Follow-up meeting requests
- **Feedback**: Positive feedback scores

### Post-Demo Actions
- **Email Follow-up**: Within 24 hours
- **Custom Demo**: Tailored to specific needs
- **Pilot Program**: Limited deployment opportunity
- **Partnership Discussion**: Business model discussion

## 🚨 Troubleshooting

### Common Issues
1. **Ollama Not Ready**: Wait for model download
2. **Database Connection**: Check Docker containers
3. **Voice Not Working**: Verify microphone permissions
4. **Slow Performance**: Check system resources

### Recovery Commands
```bash
# Reset demo environment
docker-compose -f setup/docker-compose.demo.yml down -v
docker-compose -f setup/docker-compose.demo.yml up -d

# Reinitialize data
python setup/init_demo_data.py --force

# Health check
python scripts/health_check.py --verbose
```

## 📞 Contact

For demo-related questions or support:
- **Email**: demo@krishi-sarthi.com
- **Phone**: +91-XXXX-XXXX-XXXX
- **Website**: https://krishi-sarthi.com/demo
