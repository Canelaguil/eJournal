<template>
    <b-card class="no-hover">
        <h2 class="mb-2">Group: {{ group.name }}</h2>
            <b-form v-if="$hasPermission('can_edit_course_user_group')" @submit.prevent="updateGroupName">
                <b-input class="multi-form theme-input" v-model="form.newGroupName" placeholder="Update group name" required/>
                <b-button class="float-right add-button" type="submit">
                    <icon name="plus-square"/>
                    Update
                </b-button>
            </b-form>
            <b-button v-if="$hasPermission('can_delete_course_user_group')" class="float-left delete-button" @click.prevent.stop="removeGroup()">
                <icon name="trash"/>
                Remove group
            </b-button>
    </b-card>
</template>

<script>
import icon from 'vue-awesome/components/Icon'
import groupAPI from '@/api/group'

export default {
    props: {
        cID: {
            required: true
        },
        group: {
            required: true
        }
    },
    data () {
        return {
            form: {
                newGroupName: ''
            }
        }
    },
    methods: {
        updateGroupName () {
            console.log(this.group)
            groupAPI.update(this.group.id, {
                name: this.form.newGroupName
            })
                .then(group => {
                    this.group = group
                    this.$emit('update-group', this.group)
                    this.$toasted.success('Successfully updated the group.')
                    this.form.newGroupName = ''
                })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        },
        removeGroup () {
            if (confirm('Are you sure you want to remove "' + this.group.name + '" from this course?')) {
                groupAPI.delete(this.group.id).then(data => {
                    this.$toasted.success(data.description)
                    this.$emit('delete-group', this.group)
                }, error => {
                    this.$toasted.error(error.response.data.description)
                })
            }
        }
    },
    created () {
        this.groupName = this.group
    },
    components: {
        'icon': icon
    }
}
</script>
