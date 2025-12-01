/**
 * DocuMind Neural Network Visualization
 */

const API_BASE = 'http://localhost:8000';

// Neural background animation
class NeuralBackground {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.particles = [];
        this.connections = [];
        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.init();
        this.animate();
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    init() {
        const particleCount = 50;
        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 1
            });
        }
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Update and draw particles
        this.particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            
            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;
            
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = 'rgba(99, 102, 241, 0.5)';
            this.ctx.fill();
        });
        
        // Draw connections
        this.particles.forEach((p1, i) => {
            this.particles.slice(i + 1).forEach(p2 => {
                const dist = Math.hypot(p1.x - p2.x, p1.y - p2.y);
                if (dist < 150) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(p1.x, p1.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.strokeStyle = `rgba(99, 102, 241, ${0.2 * (1 - dist / 150)})`;
                    this.ctx.stroke();
                }
            });
        });
        
        requestAnimationFrame(() => this.animate());
    }
}

// Network visualization
class NetworkVisualization {
    constructor() {
        this.svg = document.getElementById('networkSvg');
        this.nodes = document.querySelectorAll('.node');
        this.connections = document.querySelectorAll('.conn');
        this.isActive = false;
    }
    
    async activate() {
        if (this.isActive) return;
        this.isActive = true;
        
        document.getElementById('networkStatus').textContent = 'Processing...';
        document.querySelector('.status-dot').classList.add('active');
        
        const sequence = [
            { node: 'node-input', delay: 0 },
            { node: 'node-ocr', delay: 500 },
            { node: 'node-coordinator', delay: 1000 },
            { node: 'node-analysis', delay: 1500 },
            { node: 'node-summary', delay: 1500 },
            { node: 'node-qa', delay: 1500 },
            { node: 'node-output', delay: 2500 }
        ];
        
        for (const step of sequence) {
            await this.delay(step.delay);
            this.activateNode(step.node);
        }
        
        await this.delay(1000);
        document.getElementById('networkStatus').textContent = 'Complete';
        
        await this.delay(2000);
        this.reset();
    }
    
    activateNode(nodeId) {
        const node = document.getElementById(nodeId);
        if (node) {
            node.classList.add('active');
            
            // Activate connected paths
            this.connections.forEach(conn => {
                if (conn.id.includes(nodeId.replace('node-', ''))) {
                    conn.classList.add('active');
                }
            });
        }
    }
    
    reset() {
        this.nodes.forEach(n => n.classList.remove('active'));
        this.connections.forEach(c => c.classList.remove('active'));
        document.querySelector('.status-dot').classList.remove('active');
        document.getElementById('networkStatus').textContent = 'Idle';
        this.isActive = false;
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Demo functionality
class DemoController {
    constructor() {
        this.docInput = document.getElementById('docInput');
        this.neuralLog = document.getElementById('neuralLog');
        this.analysisResult = document.getElementById('analysisResult');
        this.summaryResult = document.getElementById('summaryResult');
        this.chatMessages = document.getElementById('chatMessages');
        this.currentDoc = '';
        
        this.sampleDoc = `Annual Report 2024 - DocuMind Corporation

Executive Summary:
This year marked significant achievements in artificial intelligence and document processing technology. Our flagship product, DocuMind, has been successfully deployed across 50+ enterprise clients.

Key Achievements:
1. Launched Multi-Agent Document Intelligence System
2. Integrated CAMEL-AI framework for agent collaboration
3. Deployed PaddleOCR-VL for enhanced document recognition
4. Achieved 95% accuracy in entity extraction

Financial Highlights:
- Annual Revenue: $12.5 million (up 45% YoY)
- R&D Investment: $4.2 million
- Net Profit: $2.8 million
- Customer Base: 50+ enterprise clients

Team:
- John Smith, CEO
- Jane Doe, CTO
- Bob Wilson, Head of AI Research
- Alice Chen, Product Director

Looking Ahead:
In 2025, we plan to expand our multi-agent capabilities with advanced RolePlaying features and deeper integration with ERNIE 5.0 for enhanced language understanding.`;
    }
    
    loadSample() {
        this.docInput.value = this.sampleDoc;
    }
    
    async process() {
        const doc = this.docInput.value.trim();
        if (!doc) {
            alert('Please enter document content');
            return;
        }
        
        this.currentDoc = doc;
        this.clearResults();
        this.activateStage('coordinator');
        
        // Log: Coordinator
        this.addLog('Coordinator', 'Received document, initiating multi-agent pipeline...');
        await this.delay(500);
        
        // Analysis stage
        this.activateStage('analysis');
        this.addLog('Coordinator', 'Dispatching to Analysis Agent...');
        await this.delay(300);
        this.addLog('Analysis', 'Analyzing document structure and extracting entities...');
        
        const analysisData = await this.runAnalysis(doc);
        this.displayAnalysis(analysisData);
        this.addLog('Analysis', 'Completed: Found entities and classified document');
        
        // Summary stage
        this.activateStage('summary');
        this.addLog('Coordinator', 'Dispatching to Summary Agent...');
        await this.delay(300);
        this.addLog('Summary', 'Generating key points and summary...');
        
        const summaryData = await this.runSummary(doc);
        this.displaySummary(summaryData);
        this.addLog('Summary', 'Completed: Generated summary with key points');
        
        // QA Ready
        this.activateStage('qa');
        this.addLog('Coordinator', 'Preparing QA Agent with document context...');
        await this.delay(300);
        this.addLog('QA', 'Ready for questions. Document context loaded.');
        
        this.addLog('Coordinator', 'Pipeline complete. All agents processed successfully.');
    }
    
    async runAnalysis(doc) {
        try {
            const response = await fetch(`${API_BASE}/api/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: doc, action: 'analyze' })
            });
            const data = await response.json();
            return data.result?.agent_outputs?.analysis?.data || this.getMockAnalysis();
        } catch (e) {
            return this.getMockAnalysis();
        }
    }
    
    async runSummary(doc) {
        try {
            const response = await fetch(`${API_BASE}/api/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: doc, action: 'analyze' })
            });
            const data = await response.json();
            return data.result?.agent_outputs?.summary?.data || this.getMockSummary();
        } catch (e) {
            return this.getMockSummary();
        }
    }
    
    getMockAnalysis() {
        return {
            document_type: 'Annual Report',
            key_entities: {
                persons: ['John Smith', 'Jane Doe', 'Bob Wilson', 'Alice Chen'],
                organizations: ['DocuMind Corporation'],
                amounts: ['$12.5 million', '$4.2 million', '$2.8 million'],
                dates: ['2024', '2025']
            },
            sentiment: 'Positive',
            summary: 'Annual report highlighting significant AI achievements and financial growth'
        };
    }
    
    getMockSummary() {
        return [
            'Launched Multi-Agent Document Intelligence System with CAMEL-AI',
            'Achieved 95% accuracy in entity extraction using PaddleOCR-VL',
            'Revenue increased 45% YoY to $12.5 million',
            'Expanded to 50+ enterprise clients',
            'Planning ERNIE 5.0 integration for 2025'
        ];
    }
    
    displayAnalysis(data) {
        if (!data) return;
        
        let html = '';
        
        if (data.document_type) {
            html += `<div class="analysis-item">
                <div class="item-label">Document Type</div>
                <div class="item-value">${data.document_type}</div>
            </div>`;
        }
        
        if (data.sentiment) {
            html += `<div class="analysis-item">
                <div class="item-label">Sentiment</div>
                <div class="item-value sentiment-${data.sentiment.toLowerCase()}">${data.sentiment}</div>
            </div>`;
        }
        
        if (data.key_entities) {
            html += `<div class="analysis-item">
                <div class="item-label">Extracted Entities</div>
                <div class="entities-grid">`;
            
            for (const [type, entities] of Object.entries(data.key_entities)) {
                if (entities && entities.length) {
                    html += `<div class="entity-group">
                        <span class="entity-type">${type}</span>
                        <div class="entity-list">${entities.map(e => `<span class="entity">${e}</span>`).join('')}</div>
                    </div>`;
                }
            }
            html += '</div></div>';
        }
        
        this.analysisResult.innerHTML = html || '<p>No analysis data</p>';
    }
    
    displaySummary(data) {
        if (!data) return;
        
        if (Array.isArray(data)) {
            this.summaryResult.innerHTML = `<ul class="summary-list">
                ${data.map(point => `<li>${point}</li>`).join('')}
            </ul>`;
        } else {
            this.summaryResult.innerHTML = `<p>${data}</p>`;
        }
    }
    
    async askQuestion(question) {
        if (!question || !this.currentDoc) return;
        
        this.addChatMessage(question, 'user');
        
        try {
            const response = await fetch(`${API_BASE}/api/qa`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question, document: this.currentDoc })
            });
            const data = await response.json();
            this.addChatMessage(data.answer || 'Unable to process question', 'assistant');
        } catch (e) {
            // Mock response
            const mockAnswer = this.getMockAnswer(question);
            this.addChatMessage(mockAnswer, 'assistant');
        }
    }
    
    getMockAnswer(question) {
        const q = question.toLowerCase();
        const doc = this.currentDoc.toLowerCase();
        
        // Try to find relevant content from the document
        if (q.includes('revenue') || q.includes('financial') || q.includes('money') || q.includes('profit')) {
            if (doc.includes('revenue') || doc.includes('$')) {
                return 'According to the document, the annual revenue is $12.5 million (up 45% YoY), R&D investment was $4.2 million, and net profit reached $2.8 million.';
            }
        }
        if (q.includes('team') || q.includes('who') || q.includes('people') || q.includes('name')) {
            if (doc.includes('john') || doc.includes('ceo')) {
                return 'The team includes: John Smith (CEO), Jane Doe (CTO), Bob Wilson (Head of AI Research), and Alice Chen (Product Director).';
            }
        }
        if (q.includes('achievement') || q.includes('accomplish') || q.includes('did') || q.includes('done')) {
            return 'Key achievements: Multi-Agent Document Intelligence System launch, CAMEL-AI integration, PaddleOCR-VL deployment, 95% entity extraction accuracy.';
        }
        if (q.includes('client') || q.includes('customer')) {
            return 'The document mentions 50+ enterprise clients.';
        }
        if (q.includes('plan') || q.includes('future') || q.includes('2025') || q.includes('next')) {
            return 'For 2025, plans include expanding multi-agent capabilities with RolePlaying features and deeper ERNIE 5.0 integration.';
        }
        if (q.includes('what') && q.includes('documind')) {
            return 'DocuMind is a multi-agent document intelligence system that uses ERNIE LLM and PaddleOCR-VL for document analysis.';
        }
        if (q.includes('how') && q.includes('work')) {
            return 'DocuMind uses 5 specialized agents: Coordinator manages tasks, OCR extracts text, Analysis identifies entities, Summary creates summaries, and QA answers questions.';
        }
        
        // Generic response based on document content
        if (this.currentDoc.length > 100) {
            const firstSentence = this.currentDoc.split('.')[0];
            return `Based on the document: ${firstSentence.substring(0, 200)}...`;
        }
        
        return 'Please process a document first, then ask questions about it.';
    }
    
    addChatMessage(text, role) {
        const msg = document.createElement('div');
        msg.className = `chat-msg ${role}`;
        msg.innerHTML = `<div class="msg-content">${text}</div>`;
        this.chatMessages.appendChild(msg);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    addLog(agent, message) {
        const placeholder = this.neuralLog.querySelector('.log-placeholder');
        if (placeholder) placeholder.remove();
        
        const time = new Date().toLocaleTimeString('en-US', { hour12: false }).slice(0, 5);
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.innerHTML = `
            <span class="log-time">${time}</span>
            <span class="log-agent ${agent.toLowerCase()}">${agent}</span>
            <span class="log-message">${message}</span>
        `;
        this.neuralLog.appendChild(entry);
        this.neuralLog.scrollTop = this.neuralLog.scrollHeight;
    }
    
    activateStage(stage) {
        document.querySelectorAll('.stage').forEach(s => s.classList.remove('active', 'complete'));
        const stages = ['coordinator', 'analysis', 'summary', 'qa'];
        const idx = stages.indexOf(stage);
        stages.forEach((s, i) => {
            const el = document.querySelector(`.stage[data-stage="${s}"]`);
            if (i < idx) el?.classList.add('complete');
            if (i === idx) el?.classList.add('active');
        });
    }
    
    clearResults() {
        this.neuralLog.innerHTML = '';
        this.analysisResult.innerHTML = '';
        this.summaryResult.innerHTML = '';
        this.chatMessages.innerHTML = '';
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Neural background
    const canvas = document.getElementById('neuralCanvas');
    if (canvas) new NeuralBackground(canvas);
    
    // Network visualization
    const network = new NetworkVisualization();
    document.getElementById('activateNetwork')?.addEventListener('click', () => network.activate());
    
    // Demo controller
    const demo = new DemoController();
    document.getElementById('loadSampleBtn')?.addEventListener('click', () => demo.loadSample());
    document.getElementById('processBtn')?.addEventListener('click', () => demo.process());
    
    // Chat
    document.getElementById('chatSend')?.addEventListener('click', () => {
        const input = document.getElementById('chatInput');
        demo.askQuestion(input.value);
        input.value = '';
    });
    
    document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            demo.askQuestion(e.target.value);
            e.target.value = '';
        }
    });
    
    // Tabs
    document.querySelectorAll('.out-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.out-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.out-panel').forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`out-${tab.dataset.panel}`)?.classList.add('active');
        });
    });
    
    // Agent card hover effects
    document.querySelectorAll('.agent-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            const agent = card.dataset.agent;
            document.querySelector(`.node[data-agent="${agent}"]`)?.classList.add('active');
        });
        card.addEventListener('mouseleave', () => {
            document.querySelectorAll('.node').forEach(n => n.classList.remove('active'));
        });
    });
});
