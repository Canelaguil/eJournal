<template>
    <b-card class="no-hover settings-card" :class="$root.getBorderClass($route.params.cID)">
        <h2>Assignment details</h2>
        <b-form @submit.prevent="onSubmit">
            <h2 class="field-heading">Assignment name</h2>
            <b-input class="multi-form theme-input"
                     v-model="assignmentDetails.name"
                     placeholder="Assignment name"
                     @change="$emit('changed')"/>
            <h2 class="field-heading">Description</h2>
            <text-editor class="multi-form"
                :id="'text-editor-assignment-edit-description'"
                :givenContent="assignmentDetails.description"
                @content-update="assignmentDetails.description = $event"
                @change="$emit('changed')"
                :footer="false"/>
            <h2 class="field-heading">Points possible</h2>
            <b-input class="multi-form theme-input"
                v-model="assignmentDetails.points_possible"
                placeholder="Points"
                @change="$emit('changed')"
                type="number"/>
            <b-row>
                <b-col xl="4">
                    <h2 class="field-heading">Unlock date</h2>
                    <flat-pickr class="multi-form theme-input full-width"
                    v-model="assignmentDetails.unlock_date"
                    @on-change="$emit('changed')"
                    :config="$root.flatPickrTimeConfig"/>
                </b-col>
                <b-col xl="4">
                    <h2 class="field-heading">Due date</h2>
                    <flat-pickr class="multi-form theme-input full-width"
                    v-model="assignmentDetails.due_date"
                    @on-change="$emit('changed')"
                    :config="$root.flatPickrTimeConfig"/>
                </b-col>
                <b-col xl="4">
                    <h2 class="field-heading">Lock date</h2>
                    <flat-pickr class="multi-form theme-input full-width"
                    v-model="assignmentDetails.lock_date"
                    @on-change="$emit('changed')"
                    :config="$root.flatPickrTimeConfig"/>
                </b-col>
            </b-row>
        </b-form>
    </b-card>
</template>

<script>
import textEditor from '@/components/assets/TextEditor.vue'
import icon from 'vue-awesome/components/Icon'

export default {
    name: 'FormatEditAssignmentDetailsCard',
    props: {
        assignmentDetails: {
            required: true
        }
    },
    components: {
        'text-editor': textEditor,
        icon
    }
}
</script>
