const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const port = 3000;

app.use(cors());
app.use(express.static('public'));

app.get('/file-list', (req, res) => {
    const folderPath = '02-29-2024';

    fs.readdir(folderPath, (err, files) => {
        if (err) {
            console.error('Error reading the directory:', err);
            return res.status(500).send('Error reading the directory.');
        }

        // Filter out only .wav files
        const wavFiles = files.filter(file => path.extname(file).toLowerCase() === '.wav');

        // Create anchor links for each .wav file
        const fileLinks = wavFiles.map(fileName => `<a href="/audio/${fileName}">${fileName}</a>`);

        res.send(fileLinks.join('<br>'));
    });
});

app.get('/audio/:fileName', (req, res) => {
    const folderPath = '02-29-2024';
    const fileName = req.params.fileName;
    const wavFilePath = path.join(__dirname, folderPath, fileName);
    const txtFileName = `${path.parse(fileName).name}.txt`.replace('_trimmed', '');
    const txtFilePath = path.join(__dirname, folderPath, txtFileName);

    // Read content from the associated .txt file
    let txtFileContent = '';
    if (fs.existsSync(txtFilePath)) {
        txtFileContent = fs.readFileSync(txtFilePath, 'utf-8');
    }

    // Get a list of all .wav files in the folder
    const allWavFiles = fs.readdirSync(path.join(__dirname, folderPath))
        .filter(file => path.extname(file).toLowerCase() === '.wav');

    // Find the index of the current file in the list
    const currentIndex = allWavFiles.findIndex(file => file === fileName);

    // Calculate the next and previous indexes
    const nextIndex = (currentIndex + 1) % allWavFiles.length;
    const prevIndex = (currentIndex - 1 + allWavFiles.length) % allWavFiles.length;

    // Serve an HTML page with an audio player, associated .txt file content, and next/previous buttons
    res.send(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Audio Player</title>
        </head>
        <body>
            <h1>Audio Player: ${fileName}</h1>
            <audio controls>
                <source src="/audio-file/${fileName}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
            <div>
                <h2>Associated Text Content</h2>
                <p>${txtFileContent}</p>
            </div>
            <div>
                <a href="/audio/${allWavFiles[prevIndex]}">Previous</a>
                <span> | </span>
                <a href="/audio/${allWavFiles[nextIndex]}">Next</a>
            </div>
        </body>
        </html>
    `);
});

app.get('/audio-file/:fileName', (req, res) => {
    const fileName = req.params.fileName;
    const filePath = path.join(__dirname, '02-29-2024', fileName);

    // Serve the requested .wav file
    res.sendFile(filePath);
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});

