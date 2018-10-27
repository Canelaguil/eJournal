<!-- Custom wrapper for tinymce editor -->
<!-- If more events are desired, here is an overview: https://www.tiny.cloud/docs/advanced/events/ -->

<!-- TODO displayInline functionality not compatible with launching the editor from a modal -->

<template>
    <div class="editor-container" >
        <textarea :id="id"/>
    </div>
</template>

<script>
// TODO Figure out why importing tinymce gives a warning transferred with MIME type 2x
import tinymce from 'tinymce/tinymce'
import 'tinymce/themes/modern/theme'
import 'tinymce/skins/lightgray/skin.min.css'

/* Only works with basic lists enabled. */
import 'tinymce/plugins/advlist'
import 'tinymce/plugins/autolink'
import 'tinymce/plugins/autoresize'
import 'tinymce/plugins/autosave'
/* Allows direct manipulation of the html aswell as easy export. */
import 'tinymce/plugins/code'
import 'tinymce/plugins/colorpicker'
import 'tinymce/plugins/fullscreen'
import 'tinymce/plugins/image'
import 'tinymce/plugins/imagetools'
import 'tinymce/plugins/link'
import 'tinymce/plugins/lists'
import 'tinymce/plugins/nonbreaking'
import 'tinymce/plugins/media'
import 'tinymce/plugins/preview'
import 'tinymce/plugins/paste'
import 'tinymce/plugins/print'
import 'tinymce/plugins/hr'
import 'tinymce/plugins/searchreplace'
import 'tinymce/plugins/spellchecker'
import 'tinymce/plugins/table'
import 'tinymce/plugins/textcolor'
import 'tinymce/plugins/textpattern'
/* Table of contents. */
import 'tinymce/plugins/toc'
import 'tinymce/plugins/wordcount'

export default {
    name: 'TextEditor',
    props: {
        limitedColors: {
            type: Boolean,
            default: false
        },
        basic: {
            type: Boolean,
            default: false
        },
        /* Used to bind the editor to the components text area. */
        id: {
            type: String,
            required: true
        },
        givenContent: {
            type: String,
            default: ''
        },
        displayInline: {
            default: false
        },
        footer: {
            default: true
        },
        placeholderText: {
            type: String,
            default: ''
        }
    },
    data () {
        return {
            content: '',
            placeholderStatus: false,
            initPlaceholder: false,
            placeholder: '',
            editor: null,
            config: {
                selector: '#' + this.id,
                init_instance_callback: this.editorInit,

                paste_data_images: true,
                /* https://www.tiny.cloud/docs/configure/file-image-upload/#images_dataimg_filter
                 * Disables conversion of base64 images into blobs, only used when pasting an image. */
                images_dataimg_filter: function (img) {
                    return img.hasAttribute('internal-blob')
                },

                menubar: true,
                branding: false,
                statusbar: true,
                inline: false,
                image_title: true,

                autosave_ask_before_unload: true,
                autosave_interval: '10s',
                autosave_restore_when_empty: true,

                /* Custom styling applied to the editor */
                content_style: `
                    @import url('https://fonts.googleapis.com/css?family=Roboto+Condensed|Roboto:400,700');
                    body {
                        font-family: "Roboto Condensed"
                    } `,

                file_picker_types: 'image',
                file_picker_callback: this.insertDataURL
            },
            basicConfig: {
                toolbar1: 'bold italic underline alignleft aligncenter alignright alignjustify | forecolor backcolor restoredraft | formatselect | bullist numlist | image media table | removeformat fullscreentoggle fullscreen',
                plugins: [
                    'autoresize paste textcolor image lists wordcount autolink autosave',
                    'table media fullscreen'
                ]
            },
            extensiveConfig: {
                toolbar1: 'bold italic underline alignleft aligncenter alignright alignjustify | forecolor backcolor | formatselect | bullist numlist | image media table | removeformat fullscreentoggle fullscreen',
                plugins: [
                    'link media preview paste print hr lists advlist wordcount autolink autosave',
                    'autoresize code fullscreen image imagetools',
                    'textcolor searchreplace table toc'
                ]
            },
            extensiveConfigMenu: {
                menu: {
                    file: {title: 'File', items: 'newdocument restoredraft print'},
                    edit: {title: 'Edit', items: 'undo redo | cut copy paste | code | selectall searchreplace'},
                    insert: {title: 'Insert', items: 'image media link | hr | toc'},
                    view: {title: 'View', items: 'preview fullscreen'},
                    format: {title: 'Format', items: 'bold italic underline strikethrough superscript subscript | blockformats align | removeformat'},
                    table: {title: 'Table', items: 'inserttable tableprops deletetable | cell row column'}
                }
            },
            fullScreenButton: null
        }
    },
    watch: {
        content: function (newVal, oldVal) {
            if (this.placeholderStatus === true) {
                var result = newVal

                if (result.includes(this.placeholderText)) {
                    result = result.replace('<span style="color: #808080;">', '')
                    result = result.replace('</span>', '')
                    result = result.replace(this.placeholderText, '')

                    /*  If there is additional input replace the placeholder
                    with with the new input. Else replace the
                    the partly deleted placeholder with the complete
                    placeholder again.  */
                    if (this.stripHtml(result).length !== 0) {
                        /*  If the resulting text contains new characters this will
                        overwrite the placeholder.  */
                        this.content = result
                        this.editor.setContent(result)
                        this.placeholderStatus = false

                        /* Sets the cursor in the end of the resulting text. */
                        this.editor.selection.select(this.editor.getBody(), true)
                        this.editor.selection.collapse(false)
                        /* Emits a change in the adapted placeholder. */
                        this.$emit('content-update', result)
                    }
                } else if (newVal.length < oldVal.length) {
                    this.content = this.placeholder
                    this.editor.setContent(this.placeholder)
                }
            } else if (this.placeholderText !== '' && newVal === '' && this.placeholderStatus === false) {
                this.content = this.placeholder
                this.editor.setContent(this.placeholder)

                this.placeholderStatus = true
                this.$emit('content-update', null)
            } else if (!this.initPlaceholder) {
                this.$emit('content-update', this.content)
            }
        },
        id: function (newID, oldID) {
            this.setPlaceholderColor(this.placeholderText)

            tinymce.EditorManager.execCommand('mceRemoveControl', true, '#' + oldID)
            this.config.selector = '#' + newID
            tinymce.init(this.config)
            tinymce.EditorManager.execCommand('mceAddControl', true, '#' + newID)

            if (this.stripHtml(this.givenContent) === '' && this.stripHtml(this.placeholder) !== '') {
                this.initPlaceholder = true
                this.content = this.placeholder
                this.editor.setContent(this.placeholder)

                this.$nextTick(function () {
                    this.placeholderStatus = true
                    this.initPlaceholder = false
                })
            } else {
                this.placeholderStatus = false
                this.content = this.givenContent
                this.editor.setContent(this.givenContent)
            }
        }
    },
    methods: {
        editorInit (editor) {
            var vm = this
            this.editor = editor

            this.setPlaceholderColor(this.placeholderText)

            if (this.stripHtml(this.givenContent) === '' && this.placeholderText !== '') {
                this.content = this.placeholder

                editor.setContent(this.placeholder)
                this.initPlaceholder = true

                this.$nextTick(function () {
                    this.placeholderStatus = true
                    this.initPlaceholder = false
                })
            } else {
                this.content = this.givenContent
                /* set content resets the default font for some reason */
                editor.setContent(this.givenContent)
            }

            if (this.displayInline) {
                this.setupInlineDisplay(editor)
            }

            editor.on('Change', (e) => {
                vm.content = this.editor.getContent()
            })

            editor.on('KeyUp', (e) => {
                vm.handleShortCuts(e)
                vm.content = this.editor.getContent()
            })

            /*  Forces the user to the first cursor place if a placeholder
                is being shown, ignores the 'cursor changes' if an action is
                done, which results in the same cursor location.    */
            if (this.placeholderText !== '') {
                editor.on('NodeChange', (e) => {
                    if (this.placeholderStatus && !this.checkFormatChange(editor)) {
                        editor.selection.setCursorLocation(editor.getBody().children[0], 0)
                    }
                })
            }
        },
        setupInlineDisplay (editor) {
            var footer = this.footer
            var vm = this

            editor.theme.panel.find('toolbar')[0].$el.hide()
            if (!this.basic) { editor.theme.panel.find('menubar')[0].$el.hide() }

            if (footer) { editor.theme.panel.find('#statusbar')[0].$el.hide() }

            editor.on('focus', function () {
                if (!vm.basic) { editor.theme.panel.find('menubar')[0].$el.show() }
                editor.theme.panel.find('toolbar')[0].$el.show()
                if (footer) { editor.theme.panel.find('#statusbar')[0].$el.show() }
            })

            editor.on('blur', function () {
                if (!vm.basic) { editor.theme.panel.find('menubar')[0].$el.hide() }
                editor.theme.panel.find('toolbar')[0].$el.hide()
                if (footer) { editor.theme.panel.find('#statusbar')[0].$el.hide() }
            })
        },
        handleShortCuts (e) {
            if (this.editor.plugins.fullscreen.isFullscreen() && e.key === 'Escape') {
                this.editor.execCommand('mceFullScreen', {skip_focus: true})
            }
        },
        insertDataURL () {
            var input = document.createElement('input')
            input.setAttribute('type', 'file')
            input.setAttribute('accept', 'image/*')
            var vm = this

            input.onchange = function () {
                var files = this.files
                if (!files.length) { return }

                var file = files[0]
                if (files[0].size > vm.$root.maxFileSizeBytes) {
                    this.$toasted.error('The selected image exceeds the maximum file size of ' + vm.$root.maxFileSizeBytes + ' bytes.')
                    return
                }

                var reader = new FileReader()
                reader.onload = function () {
                    var dataURL = reader.result
                    vm.editor.insertContent('<img src="' + dataURL + '"/>')
                }
                reader.readAsDataURL(file)
            }
            input.click()
        },
        handleFilePicking (cb, value, meta) {
            /* Client side allows for handling of files more than image types, which a plugin aslo handles.
               Adds a more intuitive browse button the image upload section. */
            var input = document.createElement('input')
            input.setAttribute('type', 'file')
            input.setAttribute('accept', 'image/*')
            // TODO Remove input after click

            input.onchange = function () {
                // TODO Some file error handling
                var file = this.files[0]

                var reader = new FileReader()
                reader.onload = function () {
                    var id = 'blobid' + (new Date()).getTime()
                    var blobCache = tinymce.activeEditor.editorUpload.blobCache
                    var base64 = reader.result.split(',')[1]
                    var blobInfo = blobCache.create(id, file, base64, file.name.replace(/\.[^/.]+$/, ''))
                    blobCache.add(blobInfo)

                    // Call the callback and populate the Title field with the file name
                    cb(blobInfo.blobUri(), { title: file.name })
                }
                reader.readAsDataURL(file)
            }
            input.click()
        },
        setCustomColors () {
            /* Enables some basic colors too chose from, inline with the websites theme colors. */
            this.config.textcolor_cols = 4
            this.config.textcolor_rows = 1
            this.config.textcolor_map = [
                '252C39', 'Theme dark blue',
                '007E33', 'Theme positive selected',
                'FF8800', 'Theme change selected',
                'CC0000', 'Theme negative selected'
            ]
        },
        setBasicConfig () {
            this.config.menubar = false
            this.config.toolbar1 = this.basicConfig.toolbar1
            this.config.plugins = this.basicConfig.plugins
        },
        setExtensiveConfig () {
            this.config.menubar = true
            this.config.toolbar1 = this.extensiveConfig.toolbar1
            this.config.plugins = this.extensiveConfig.plugins
            this.config.menu = this.extensiveConfigMenu.menu
        },
        enableTabs () {
            /* Three space tabs, breaks tabbing through table entries (choice) */
            this.config.plugins.push('nonbreaking')
            this.config.nonbreaking_force_tab = true
        },
        enableBrowserSpellchecker () {
            this.config.plugins.push('spellchecker')
            this.config.browser_spellcheck = true
        },
        enableMarkdownPatterns () {
            this.config.plugins.push('textpattern')
            this.config.textpattern_patterns = [
                {start: '*', end: '*', format: 'italic'},
                {start: '**', end: '**', format: 'bold'},
                {start: '#', format: 'h1'},
                {start: '##', format: 'h2'},
                {start: '###', format: 'h3'},
                {start: '####', format: 'h4'},
                {start: '#####', format: 'h5'},
                {start: '######', format: 'h6'},
                {start: '1. ', cmd: 'InsertOrderedList'},
                {start: '* ', cmd: 'InsertUnorderedList'},
                {start: '- ', cmd: 'InsertUnorderedList'}
            ]
        },
        clearContent () {
            this.editor.setContent('')
            this.editor.execCommand('fontName', false, 'roboto condensed', {skip_focus: true})
            this.content = ''
        },
        stripHtml (html) {
            // Create a new div element
            var temporalDivElement = document.createElement('div')
            // Set the HTML content with the providen
            temporalDivElement.innerHTML = html
            // Retrieve the text property of the element (cross-browser support)
            return temporalDivElement.textContent || temporalDivElement.innerText || ''
        },
        setPlaceholderColor () {
            this.placeholder = '<p><span style="color: #808080;">' + this.placeholderText + '</span></p>'
        },
        checkFormatChange (editor) {
            var formatList = this.config.menu.format.items
            var formats = formatList.split(' ')

            for (var i = 0; i < formats.length; i++) {
                if (editor.queryCommandState(formats[i])) {
                    return true
                }
            }

            return false
        }
    },
    mounted () {
        this.config.statusbar = this.footer

        if (this.basic) {
            this.setBasicConfig()
        } else {
            this.setExtensiveConfig()
        }

        if (this.limitedColors) {
            this.setCustomColors()
        } else {
            this.config.plugins.push('colorpicker')
        }

        this.enableTabs()
        this.enableBrowserSpellchecker()
        this.enableMarkdownPatterns()

        tinymce.init(this.config)
    },
    beforeDestroy () {
        if (this.editor) { this.editor.destroy() }
    }
}
</script>

<style lang="sass">
.editor-container
    padding-right: 1px
    width: 100%

.mce-fullscreen
    padding-top: 70px

// Assume we're in a modal
form .mce-fullscreen
    padding-top: 0px
</style>
