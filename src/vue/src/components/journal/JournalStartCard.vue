<span<template>
    <b-card class="no-hover" :class="$root.getBorderClass($route.params.cID)">
        <h2>{{ assignment.name }}</h2>
        <sandboxed-iframe v-if="assignment.description" :content="assignment.description"/>
        <h2 class="field-heading" v-if="assignment.unlock_date">Unlock date</h2>
        <span v-if="assignment.unlock_date">{{ $root.beautifyDate(assignment.unlock_date) }}</span>
        <h2 class="field-heading" v-if="assignment.unlock_date && new Date(assignment.unlock_date) > new Date()">This assignment is locked and will be made available later.</h2>
        <h2 class="field-heading" v-else-if="student && assignment.due_date && new Date(assignment.due_date) < new Date()">The deadline for this assignment has passed.</h2>
    </b-card>
</template>

<script>
import sandboxedIframe from '@/components/assets/SandboxedIframe.vue'

export default {
    props: ['assignment', 'student'],
    components: {
        sandboxedIframe
    }
}
</script>
