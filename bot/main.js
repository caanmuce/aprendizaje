const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const mysql = require('mysql2/promise');
const cron = require('node-cron');
const express = require('express');
const session = require('express-session');
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(session({
    secret: 'mi_secreto_super_seguro',
    resave: false,
    saveUninitialized: true
}));

// Servir archivos estáticos desde la carpeta 'public'
app.use(express.static(path.join(__dirname, 'public')));

// 1. Conexión MySQL
const pool = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: '', // <-- Cambia tu contraseña aquí
    database: 'citas_medicas',
    waitForConnections: true,
    connectionLimit: 10
});

// 2. Bot de WhatsApp
const client = new Client({ authStrategy: new LocalAuth() });

client.on('qr', (qr) => qrcode.generate(qr, { small: true }));
client.on('ready', () => {
    console.log('Bot de WhatsApp listo!');
    
    // Cron Job cada 1 minuto (para pruebas rápidas)
    cron.schedule('* * * * *', () => {
        revisarYEnviarRecordatorios();
    });
});

async function revisarYEnviarRecordatorios() {
    try {
        const [citas] = await pool.query(`
            SELECT c.id, c.fecha_hora, p.nombre, p.telefono
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.id
            WHERE c.fecha_hora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 24 HOUR)
              AND c.recordatorio_enviado = FALSE
        `);

        for (const cita of citas) {
            const numeroLimpio = cita.telefono.replace(/[^0-9]/g, '');
            const chatId = `${numeroLimpio}@c.us`;
            const fechaFormateada = new Date(cita.fecha_hora).toLocaleString('es-ES', {
                dateStyle: 'medium',
                timeStyle: 'short'
            });

            const mensaje = `Hola ${cita.nombre}, te recordamos que tienes una cita médica programada para el ${fechaFormateada}.`;

            await client.sendMessage(chatId, mensaje);
            console.log(`Recordatorio enviado a ${cita.nombre} (${cita.telefono})`);
            await pool.query('UPDATE citas SET recordatorio_enviado = TRUE WHERE id = ?', [cita.id]);
        }
    } catch (error) {
        console.error('Error enviando recordatorios:', error);
    }
}

// 3. Rutas API para la Web
app.post('/api/login', async (req, res) => {
    const { username, password } = req.body;
    try {
        const [rows] = await pool.query('SELECT * FROM usuarios WHERE username = ? AND password = ?', [username, password]);
        if (rows.length > 0) {
            req.session.usuario = rows[0];
            return res.json({ status: 'ok', message: 'Sesión iniciada' });
        }
        res.status(401).json({ status: 'error', message: 'Credenciales inválidas' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/agendar', async (req, res) => {
    if (!req.session.usuario) {
        return res.status(401).json({ error: 'No autorizado. Inicie sesión.' });
    }

    const { nombre, telefono, fecha_hora } = req.body;

    try {
        // Insertar o recuperar paciente
        let [paciente] = await pool.query('SELECT id FROM pacientes WHERE telefono = ?', [telefono]);
        let pacienteId;
        
        if (paciente.length === 0) {
            const [nuevo] = await pool.query('INSERT INTO pacientes (nombre, telefono) VALUES (?, ?)', [nombre, telefono]);
            pacienteId = nuevo.insertId;
        } else {
            pacienteId = paciente[0].id;
        }

        // Crear la cita
        await pool.query('INSERT INTO citas (paciente_id, fecha_hora) VALUES (?, ?)', [pacienteId, fecha_hora]);

        res.json({ status: 'ok', message: 'Cita agendada exitosamente' });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Iniciar Servidor Web
app.listen(3000, () => {
    console.log('Servidor web ejecutándose en http://localhost:3000');
});
// Servir explícitamente el archivo index.html en la ruta principal
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

client.initialize();