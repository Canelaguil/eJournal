<template>
    <div>
        <b-card class="no-hover settings-card">
            <div v-if="$hasPermission('can_add_course_user_group')">
                <h2 class="mb-2">Create new group</h2>
                <b-form @submit.prevent="createUserGroup" @reset.prevent="resetFormInput">
                    <b-input class="multi-form theme-input" v-model="form.groupName" placeholder="Desired group name" required/>
                        <b-button class="float-left change-button" type="reset">
                        <icon name="undo"/>
                        Reset
                    </b-button>
                    <b-button class="float-right add-button" type="submit">
                        <icon name="plus-square"/>
                        Create
                    </b-button>
                </b-form>
            </div>
        </b-card>

        <group-card
            @delete-group="deleteGroup"
            @update-group="updateGroup"
            v-for="g in groups"
            :key="g.id"
            :cID="cID"
            :group="g"/>
    </div>
</template>

<script>
import icon from 'vue-awesome/components/Icon'
import groupCard from '@/components/group/GroupCard.vue'
import groupApi from '@/api/group.js'

export default {
    name: 'CourseGroupModal',
    props: {
        cID: {
            required: true
        },
        groups: {
            required: true
        }
    },
    data () {
        return {
            form: {
                groupName: '',
                lti_id: ''
            }
        }
    },
    methods: {
        createUserGroup () {
            groupApi.create({
                name: this.form.groupName,
                course_id: this.cID,
                lti_id: this.lti_id
            })
                .then(group => {
                    this.$emit('create-group', group)
                    this.$toasted.success('Successfully created group.')
                    this.resetFormInput()
                })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        },
        resetFormInput (evt) {
            /* Reset our form values */
            this.form.groupName = ''
        },
        deleteGroup (group) {
            this.$emit('delete-group', group)
        },
        updateGroup (group) {
            this.$emit('update-group', group)
        }
    },
    components: {
        'icon': icon,
        'group-card': groupCard
    }
}
</script>
