<template>
    <b-card :class="color">
        <div class="float-right">
            <slot></slot>
        </div>
        <h2>{{ line1 }}</h2>
        {{ line2 }}
    </b-card>
</template>

<script>
export default {
    props: ['line1', 'line2', 'color']
}
</script>
