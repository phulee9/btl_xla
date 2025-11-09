const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use('/images', express.static(path.join(__dirname, 'images')));

// Tạo thư mục uploads nếu chưa có
if (!fs.existsSync('uploads')) {
    fs.mkdirSync('uploads');
}

// Cấu hình multer để upload file
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + '-' + file.originalname);
    }
});

const upload = multer({
    storage: storage,
    limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
    fileFilter: (req, file, cb) => {
        // SỬA LỖI: image/ chứ không phải images/
        if (file.mimetype.startsWith('image/')) {
            cb(null, true);
        } else {
            cb(new Error('Only image files are allowed!'), false);
        }
    }
});

// API endpoint để search bằng hình ảnh
app.post('/api/search', upload.single('image'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No image uploaded' });
        }

        const imagePath = req.file.path;

        // Gọi Python script để xử lý
        const python = spawn('python', ['search.py', imagePath]);

        let dataString = '';
        let errorString = '';

        python.stdout.on('data', (data) => {
            dataString += data.toString();
        });

        python.stderr.on('data', (data) => {
            errorString += data.toString();
        });

        python.on('close', (code) => {
            if (code !== 0) {
                console.error('Python Error:', errorString);
                return res.status(500).json({ error: 'Error processing image', details: errorString });
            }

            try {
                // Lọc bỏ các dòng không phải JSON (như progress bar, warning)
                const lines = dataString.split('\n');
                let jsonString = '';

                // Tìm dòng chứa JSON (bắt đầu bằng { hoặc [)
                for (let line of lines) {
                    const trimmed = line.trim();
                    if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
                        jsonString = trimmed;
                        break;
                    }
                }

                if (!jsonString) {
                    console.error('No JSON found in output:', dataString);
                    return res.status(500).json({ error: 'Invalid response from Python script' });
                }

                const result = JSON.parse(jsonString);

                // Log để debug
                console.log('Recommendations:', result.recommendations);

                res.json({
                    success: true,
                    uploadedImage: `/${imagePath}`,
                    results: result.recommendations
                });
            } catch (e) {
                console.error('Parse Error:', e);
                console.error('Raw output:', dataString);
                res.status(500).json({ error: 'Error parsing results', details: e.message });
            }
        });

    } catch (error) {
        console.error('Server Error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});