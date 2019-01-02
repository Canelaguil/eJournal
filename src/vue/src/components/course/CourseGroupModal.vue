<template>
    <div>
        <b-card class="no-hover settings-card">
            <div v-if="$hasPermission('can_add_course_user_group')">
                <h2 class="mb-2">Create new group</h2>
                <b-form @submit.prevent="createUserGroup" @reset.prevent="resetFormInput">
                    <b-input class="multi-form theme-input" v-model="form.groupName" placeholder="Desired group name" required/>
                    <b-button class="float-left multi-form mr-2 change-button" type="reset">
                        <icon name="undo"/>
                        Reset
                    </b-button>
                    <b-button class="float-right multi-form mr-2 add-button" type="submit">
                        <icon name="plus-square"/>
                        Create
                    </b-button>
                    <b-button v-if="this.lti_linked" class="float-right multi-form mr-2 default-button" type="submit"  @click.prevent.stop="getDataNoseGroups()">
                        <icon name="sync-alt"/>
                        Sync from DataNose
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
import groupAPI from '@/api/group'

export default {
    name: 'CourseGroupModal',
    props: {
        cID: {
            required: true
        },
        groups: {
            required: true
        },
        lti_id: {
            required: false
        },
        lti_linked: {
            required: false
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
        getDataNoseGroups () {
            groupAPI.getDataNose(this.cID, {customSuccessToast: 'Successfully syncronized from DataNose.'})
                .then(groups => {
                    this.$emit('update-groups', groups)
                })
        },
        createUserGroup () {
            groupAPI.create({name: this.form.groupName, course_id: this.cID, lti_id: this.lti_id},
                {customSuccessToast: 'Successfully created group.'})
                .then(group => {
                    this.$emit('create-group', group)
                    this.resetFormInput()
                })
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
