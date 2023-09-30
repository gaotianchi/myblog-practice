const txtarea = document.getElementById("body");
const submitbtn = document.getElementById("submit");



submitbtn.aaddEventListener( 'click', () => {
    const editorData = editor.getData();

    txtarea.value = editorData;
});