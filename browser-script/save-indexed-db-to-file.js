function exportIndexedDB(dbName, storeName) {
    return new Promise((resolve, reject) => {
        let request = indexedDB.open(dbName);

        request.onsuccess = function(event) {
            let db = event.target.result;
            let transaction = db.transaction(storeName, 'readonly');
            let objectStore = transaction.objectStore(storeName);
            let allRecords = objectStore.getAll();

            allRecords.onsuccess = function() {
                // Сортировка объектов по числовому значению в конце id
                let sortedData = allRecords.result.sort((a, b) => {
                    let idA = a.id.match(/\d+$/);
                    let idB = b.id.match(/\d+$/);
                    return idA - idB;
                });

                let data = JSON.stringify(sortedData);
                let blob = new Blob([data], { type: 'application/json' });
                let url = URL.createObjectURL(blob);
                let a = document.createElement('a');
                a.href = url;
                a.download = `${dbName}_${storeName}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                resolve();
            };

            allRecords.onerror = function() {
                reject('Error retrieving data from IndexedDB');
            };
        };

        request.onerror = function() {
            reject('Error opening IndexedDB');
        };
    });
}

// Использование:
exportIndexedDB('https%3A%2F%2Fweb.telegram.org%2Fa%2F%23-1001113344905_1716364763950', 'contentStore')
    .then(() => console.log('Data export complete'))
    .catch((error) => console.error('Error exporting data:', error));
