// ================================
// Bible Reader
// ================================

const bible = new Map();

const books = [];

const searchIndex = [];

let currentBook = 0;
let currentChapter = 0;

// -------------------------------
// DOM
// -------------------------------

const chapterDiv = document.getElementById("chapter");
const chapterList = document.getElementById("chapterList");
const reference = document.getElementById("reference");
const bookList = document.getElementById("bookList");
const searchInput = document.getElementById("searchInput");
const searchResults = document.getElementById("searchResults");

// ================================
// Load All Books
// ================================

async function loadBible(){

    const list = await fetch("data/books.json")
        .then(r=>r.json());

    books.push(...list);

    for(const file of books){

        const data = await fetch(
            `data/${file}.json`
        ).then(r=>r.json());

        bible.set(file,data);

    }

    buildSidebar();

    openBook(0);

    buildSearchIndex();

}

function buildSidebar(){

    bookList.innerHTML="";

    books.forEach((file,index)=>{

        const data=bible.get(file);

        const div=document.createElement("div");

        div.className="book";

        div.textContent=data.name;

        div.onclick=()=>{

            openBook(index);

        };

        bookList.appendChild(div);

    });

}

function openBook(index){

    currentBook=index;

    currentChapter=0;

    document
    .querySelectorAll(".book")
    .forEach((b,i)=>{

        b.classList.toggle(
            "active",
            i===index
        );

    });

    buildChapterButtons();

    renderChapter();

}

function buildChapterButtons(){

    chapterList.innerHTML="";

    const data=bible.get(
        books[currentBook]
    );

    data.chapters.forEach((_,i)=>{

        const btn=
        document.createElement("button");

        btn.className="chapter-button";

        btn.textContent=i+1;

        btn.onclick=()=>{

            currentChapter=i;

            renderChapter();

            buildChapterButtons();

        };

        if(i===currentChapter)

            btn.classList.add("active");

        chapterList.appendChild(btn);

    });

}

function renderChapter(){

    const data=bible.get(
        books[currentBook]
    );

    reference.textContent=

        `${data.name} ${currentChapter+1}`;

    chapterDiv.innerHTML="";

    data.chapters[currentChapter].forEach((verse) => {

    const div = document.createElement("div");

    div.className = "verse";

    div.innerHTML = `
        <span class="verse-number">${verse.verse}</span>
        ${verse.text}
    `;

    chapterDiv.appendChild(div);

});
}

// ===========================================
// Build Search Index
// ===========================================

function buildSearchIndex() {

    searchIndex.length = 0;

    books.forEach((file, bookIndex) => {

        const book = bible.get(file);

        book.chapters.forEach((chapter, chapterIndex) => {

            chapter.forEach((verse) => {

    searchIndex.push({

        bookIndex,

        chapterIndex,

        verseIndex: verse.verse - 1,

        book: book.name,

        reference: `${book.name} ${chapterIndex + 1}:${verse.verse}`,

        text: verse.text,

        lower: verse.text.toLowerCase()

    });

});        });

    });

}

// ===========================================
// Highlight Search Text
// ===========================================

function highlight(text, query) {

    if (!query)
        return text;

    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

    const regex = new RegExp(escaped, "gi");

    return text.replace(regex, "<mark>$&</mark>");

}

// ===========================================
// Search Entire Bible
// ===========================================

function searchBible(query) {

    query = query.trim().toLowerCase();

    searchResults.innerHTML = "";

    if (query.length === 0)
        return;

    const results = searchIndex.filter(v =>
        v.lower.includes(query)
    );

    if (results.length === 0) {

        searchResults.innerHTML =
            "<div class='result'>No results found.</div>";

        return;

    }

    results.slice(0, 100).forEach(result => {

        const div = document.createElement("div");

        div.className = "result";

        div.innerHTML = `
            <div class="result-title">
                ${result.reference}
            </div>

            <div class="result-text">
                ${highlight(result.text, query)}
            </div>
        `;

        div.onclick = () => {

            currentBook = result.bookIndex;
            currentChapter = result.chapterIndex;

            buildSidebar();
            buildChapterButtons();
            renderChapter();

            searchResults.innerHTML = "";
            searchInput.value = "";

            // highlight selected verse

            setTimeout(() => {

                const verses =
                    document.querySelectorAll(".verse");

                const target =
                    verses[result.verseIndex];

                if (!target)
                    return;

                target.classList.add("highlight");

                target.scrollIntoView({

                    behavior: "smooth",

                    block: "center"

                });

                setTimeout(() => {

                    target.classList.remove("highlight");

                }, 3000);

            }, 100);

        };

        searchResults.appendChild(div);

    });

}

// ===========================================
// Search Box
// ===========================================

searchInput.addEventListener("input", e => {

    searchBible(e.target.value);

});

// ===========================================
// Previous Chapter
// ===========================================

document
.getElementById("prevChapter")
.onclick = () => {

    if (currentChapter > 0) {

        currentChapter--;

    } else if (currentBook > 0) {

        currentBook--;

        const book =
            bible.get(books[currentBook]);

        currentChapter =
            book.chapters.length - 1;

    } else {

        return;

    }

    buildSidebar();
    buildChapterButtons();
    renderChapter();

};

// ===========================================
// Next Chapter
// ===========================================

document
.getElementById("nextChapter")
.onclick = () => {

    const book =
        bible.get(books[currentBook]);

    if (currentChapter < book.chapters.length - 1) {

        currentChapter++;

    } else if (currentBook < books.length - 1) {

        currentBook++;

        currentChapter = 0;

    } else {

        return;

    }

    buildSidebar();
    buildChapterButtons();
    renderChapter();

};

// ===========================================
// Previous Book
// ===========================================

document
.getElementById("prevBook")
.onclick = () => {

    if (currentBook === 0)
        return;

    openBook(currentBook - 1);

};

// ===========================================
// Next Book
// ===========================================

document
.getElementById("nextBook")
.onclick = () => {

    if (currentBook >= books.length - 1)
        return;

    openBook(currentBook + 1);

};

// ===========================================
// Dark Mode
// ===========================================

const darkModeButton =
    document.getElementById("darkMode");

if (localStorage.getItem("dark") === "true") {

    document.body.classList.add("dark");

}

darkModeButton.onclick = () => {

    document.body.classList.toggle("dark");

    localStorage.setItem(

        "dark",

        document.body.classList.contains("dark")

    );

};

// ===========================================
// Keyboard Shortcuts
// ===========================================

document.addEventListener("keydown", e => {

    // Ignore shortcuts while typing
    if (
        document.activeElement.tagName === "INPUT" ||
        document.activeElement.tagName === "TEXTAREA"
    ) {
        if (e.key === "Escape") {
            document.activeElement.blur();
        }
        return;
    }

    switch (e.key) {

        case "/":

            e.preventDefault();

            searchInput.focus();

            break;

        case "ArrowLeft":

            document
                .getElementById("prevChapter")
                .click();

            break;

        case "ArrowRight":

            document
                .getElementById("nextChapter")
                .click();

            break;

    }

});

// ===========================================
// Start App
// ===========================================

loadBible();
