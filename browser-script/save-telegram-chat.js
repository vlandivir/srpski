async function saveContentAndScroll() {
    let db;
    let savedCount = 0;
    let processedIds = new Set();

    // Escape the full current location (URL) and add current timestamp for use as database name
    let dbName = encodeURIComponent(window.location.href) + '_' + Date.now();
    let collectionName = 'contentStore';

    // Open or create the IndexedDB
    let request = indexedDB.open(dbName, 1);
    request.onupgradeneeded = function(event) {
        db = event.target.result;
        if (!db.objectStoreNames.contains(collectionName)) {
            db.createObjectStore(collectionName, { keyPath: 'id' });
        }
    };

    request.onsuccess = function(event) {
        db = event.target.result;
        processContent();
    };

    request.onerror = function(event) {
        console.error('Error opening IndexedDB:', event);
    };

    async function processContent() {
        let elements = document.querySelectorAll('.Message');
        let transaction = db.transaction(collectionName, 'readwrite');
        let store = transaction.objectStore(collectionName);

        elements.forEach((element, index) => {
            let id = element.getAttribute('id') || index.toString(); // Use element's id or index if id is not available
            if (!processedIds.has(id)) {
                let content = element.innerHTML;
                let request = store.put({ id: id, content: content });
                request.onsuccess = function() {
                    processedIds.add(id);
                    savedCount++;
                };
                request.onerror = function(event) {
                    console.error('Error saving content:', event);
                };
            }
        });

        transaction.oncomplete = function() {
            scrollAndRepeat();
        };

        transaction.onerror = function(event) {
            console.error('Transaction error:', event);
        };
    }

    function scrollAndRepeat() {
        let triggerElement = document.querySelector('.backwards-trigger');
        if (triggerElement) {
            triggerElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => {
                let newElements = document.querySelectorAll('.Message');
                let newElementsProcessed = Array.from(newElements).filter(
                    element => !processedIds.has(element.getAttribute('id') || element.index.toString())
                );

                if (newElementsProcessed.length > 0) {
                    processContent();
                } else {
                    db.close(); // Close the connection before resolving
                    resolvePromise();
                }
            }, 1000);
        } else {
            db.close(); // Close the connection before resolving
            resolvePromise();
        }
    }

    let resolvePromise;
    const promise = new Promise((resolve) => {
        resolvePromise = resolve;
    });

    return promise.then(() => savedCount);
}

// Использование:
saveContentAndScroll().then((savedCount) => {
    console.log(`Number of saved objects: ${savedCount}`);
}).catch((error) => {
    console.error('Error:', error);
});
