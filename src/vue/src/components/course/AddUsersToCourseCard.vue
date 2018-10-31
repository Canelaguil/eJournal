<template>
    <b-card :class="$root.getBorderClass(user.id)" class="no-hover">
        <div class="float-left">
            <b>{{ user.fullname }}</b><br>
            {{ user.username }}
        </div>
        <b-button v-if="$hasPermission('can_add_course_users')"
                  @click.prevent.stop="addUserToCourse()"
                  class="add-button float-right">
            <icon name="user-plus"/>
                Add
        </b-button>
    </b-card>
</template>

<script>
import participationAPI from '@/api/participation'
import icon from 'vue-awesome/components/Icon'

export default {
    props: {
        cID: {
            required: true
        },
        user: {
            required: true
        }
    },
    methods: {
        addUserToCourse () {
            if (confirm('Are you sure you want to add "' + this.user.fullname + '" to this course?')) {
                participationAPI.create({course_id: this.cID, user_id: this.user.id})
                    .then(_ => { this.$emit('add-participant', this.user) })
            }
        }
    },
    components: {
        icon
    }
}
</script>
