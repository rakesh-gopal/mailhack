const {
    app,
    BrowserWindow,
    ipcMain
} = require("electron");

const path = require('path');
const url = require('url');

var db = require("knex")({
    client: "sqlite3",
    connection: {
        filename: path.join(__dirname, 'database.sqlite')
    },
    useNullAsDefault: true
});

app.on("ready", () => {
    let mainWindow = new BrowserWindow({
        height: 500,
        width: 500,
        show: false
    });
    mainWindow.loadURL(url.format({
        pathname: path.join(__dirname, 'main.html'),
        protocol: 'file',
        slashes: true
    }));
    mainWindow.once("ready-to-show", () => {
        mainWindow.show();
    });

    ipcMain.on("mainWindowLoaded", function() {
        let result = db.select().from("User");
        result.then(function(rows) {
            mainWindow.webContents.send("resultSent", rows);
        });
    });
    
    ipcMain.on("addUser", function(evt, user) {
        db.insert(user).into('User').then(() => {
            console.log('inserted user', user);
        });
    });
});



app.on("window-all-closed", () => {
    app.quit();
});
