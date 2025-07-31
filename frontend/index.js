const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');
const fs = require('fs');

const app = express();
const port = 3000;

const upload = multer({ dest: 'uploads/' });

// Parse JSON bodies
app.use(express.json());

// Настройки AWS для LocalStack
const s3 = new AWS.S3({
  endpoint: process.env.AWS_ENDPOINT || 'http://localhost:4566',
  region: 'eu-central-1',
  accessKeyId: 'test',
  secretAccessKey: 'test',
  s3ForcePathStyle: true,
});

// Статические HTML файлы
app.use(express.static('public'));

// Endpoint для получения уведомлений от inspector
app.post('/notify', (req, res) => {
  const { filename, size } = req.body;
  console.log(`📁 Файл загружен: ${filename}, размер: ${size} байт`);
  
  // Здесь можно добавить логику для отображения информации пользователю
  // Например, сохранить в переменную или отправить через WebSocket
  
  res.json({ success: true, message: 'Уведомление получено' });
});

// Загружаем файл в S3
app.post('/upload', upload.single('file'), (req, res) => {
  // Check if file was uploaded
  if (!req.file) {
    return res.status(400).send('No file uploaded. Please select a file.');
  }

  const file = req.file;
  const bucketName = process.env.BUCKET_NAME || 'localstack-bucket';

  const fileStream = fs.createReadStream(file.path);

  const params = {
    Bucket: bucketName,
    Key: file.originalname,
    Body: fileStream,
  };

  s3.upload(params, (err, data) => {
    fs.unlinkSync(file.path); // удалим файл после загрузки

    if (err) {
      console.error('Ошибка загрузки в S3:', err);
      return res.status(500).send('Ошибка загрузки');
    }

    console.log('Файл успешно загружен:', data.Location);
    res.send('Файл загружен в S3!');
  });
});

app.listen(port, () => {
  console.log(`Frontend работает на http://localhost:${port}`);
});
