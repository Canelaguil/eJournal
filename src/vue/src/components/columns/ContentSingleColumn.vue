<template>
    <b-row no-gutters>
        <b-col lg="8" xl="6" offset-lg="2" offset-xl="3" :class="'main-content ' + extraClasses">
            <slot/>
        </b-col>
    </b-row>
</template>

<script>
export default {
    name: 'ContentColumn',
    props: {
        extraClasses: {
            default: ''
        }
    }
}
</script>
