const watchdog = new CKSource.EditorWatchdog();

window.watchdog = watchdog;

watchdog.setCreator( ( element, config ) => {
	return CKSource.Editor
		.create( element, config )
		.then( editor => {
			// Set a custom container for the toolbar.
			document.querySelector( '.document-editor__toolbar' ).appendChild( editor.ui.view.toolbar.element );
			document.querySelector( '.ck-toolbar' ).classList.add( 'ck-reset_all' );

			return editor;
		} );
} );

watchdog.setDestructor( editor => {
	// Remove a custom container from the toolbar.
	document.querySelector( '.document-editor__toolbar' ).removeChild( editor.ui.view.toolbar.element );

	return editor.destroy();
} );

watchdog.on( 'error', handleSampleError );

watchdog
	.create( document.querySelector( '.editor' ), {
		// Editor configuration.
	} )
	.catch( handleSampleError );

function handleSampleError( error ) {
	const issueUrl = 'https://github.com/ckeditor/ckeditor5/issues';

	const message = [
		'Oops, something went wrong!',
		`Please, report the following error on ${ issueUrl } with the build id "sxf4ihsb8xp6-nnvu6gjhsxd8" and the error stack trace:`
	].join( '\n' );

	console.error( message );
	console.error( error );
}
