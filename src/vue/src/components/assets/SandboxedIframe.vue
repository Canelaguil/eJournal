<template>
    <iframe
        @load="init($event)"
        sandbox="allow-same-origin"
        frameBorder="0"
        marginwidth="0"
        marginheight="0"
        scrolling="no"
        class="w-100 theme-iframe"
    />
</template>

<script>
export default {
    name: 'SandboxedIframe',
    props: {
        content: {
            type: String,
            required: true
        }
    },
    methods: {
        scaleIframe (obj) {
            obj.height = 0
            obj.height = obj.contentWindow.document.body.offsetHeight + 'px'
        },
        injectContent (obj) {
            var doc = obj.contentWindow.document
            doc.open()
            doc.write(this.content)
            doc.close()
        },
        setCustomStyle (obj) {
            var doc = obj.contentWindow.document

            var css = `
body {
    font-family: 'Roboto', sans-serif;
    color: #252C39;
}

p a {
    text-decoration: none;
    color: #22648A;
}`

            var style = document.createElement('style')
            style.type = 'text/css'
            style.appendChild(document.createTextNode(css))
            doc.head.append(style)
        },
        init (e) {
            this.injectContent(e.target)
            this.setCustomStyle(e.target)
            this.scaleIframe(e.target)
        }
    }
}
</script>
