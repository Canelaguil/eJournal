<template>
    <b-row no-gutters>
        <b-col lg="8" xl="6" offset-xl="3" class="main-content">
            <slot name="main-content-column"></slot>
        </b-col>
        <b-col lg="4" xl="3" class="right-content">
            <slot name="right-content-column"></slot>
        </b-col>
    </b-row>
</template>

<script>
export default {
    name: 'ContentColumns'
}
</script>
