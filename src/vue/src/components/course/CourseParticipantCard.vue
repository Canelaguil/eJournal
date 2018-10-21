<template>
    <b-card :class="$root.getBorderClass(user.id)" class="no-hover">
        <b-row>
            <b-col sm="8" class="d-flex mb-2">
                <b-col cols="3" class="text-center">
                    <profile-picture class="profile-picture" :user="user"/>
                </b-col>
                <b-col cols="9">
                    <b>{{ user.name }}</b> ({{ user.role }})<br/>
                    {{ user.username }}
                </b-col>
            </b-col>
            <b-col sm="4">
                <div>
                    <b-form-select v-if="$hasPermission('can_edit_course_user_group')"
                                   v-model="selectedGroup"
                                   :select-size="1">
                        <option :value="null">No group</option>
                        <option v-for="g in groups" :key="g.name" :value="g.name">
                            {{ g.name }}
                        </option>
                    </b-form-select>
                </div>
                <div :class="{ 'input-disabled': numTeachers === 1 && selectedRole === 'Teacher'}">
                    <b-form-select v-if="$hasPermission('can_edit_course_roles')"
                                   v-model="selectedRole"
                                   :select-size="1">
                        <option v-for="r in roles" :key="r.name" :value="r.name">
                            {{ r.name }}
                        </option>
                    </b-form-select>
                <b-button v-if="$hasPermission('can_delete_course_users')"
                          @click.prevent.stop="removeFromCourse()"
                          class="delete-button full-width">
                    <icon name="user-times"/>
                    Remove
                </b-button>
                </div>
            </b-col>
        </b-row>
    </b-card>
</template>

<script>
import icon from 'vue-awesome/components/Icon'
import profilePicture from '@/components/assets/ProfilePicture.vue'

import participationAPI from '@/api/participation'

export default {
    props: {
        cID: {
            required: true
        },
        user: {
            required: true
        },
        roles: {
            required: true
        },
        group: {
            required: true
        },
        groups: {
            required: true
        },
        numTeachers: {
            required: true
        }
    },
    data () {
        return {
            selectedRole: '',
            selectedGroup: '',
            init: 2
        }
    },
    methods: {
        removeFromCourse () {
            if (confirm('Are you sure you want to remove "' + this.user.name + '" from this course?')) {
                participationAPI.delete(this.cID, this.user.id).then(data => {
                    this.$toasted.success(data.description)
                    if (this.$store.getters['user/uID'] === this.user.id) {
                        this.$store.dispatch('user/populateStore').catch(_ => {
                            this.$toasted.error('The website might be out of sync, please login again.')
                        })
                        this.$router.push({name: 'Home'})
                    }
                    this.$emit('delete-participant', this.user)
                }, error => {
                    this.$toasted.error(error.response.data.description)
                })
            }
        }
    },
    watch: {
        selectedRole (val) {
            if (this.init > 0) {
                this.init--
            } else {
                this.selectedRole = val
                this.$emit('update:role', val)
                this.$emit('update-participants', val, this.user.id)
                participationAPI.update(this.cID, {user_id: this.user.id, role: this.selectedRole, group: this.selectedGroup}).then(_ => {
                    if (this.$store.getters['user/uID'] === this.user.id) {
                        this.$store.dispatch('user/populateStore').then(_ => {
                            this.$router.push({name: 'Course', params: {cID: this.cID}})
                        }, _ => {
                            this.$toasted.error('The website might be out of sync, please login again.')
                        })
                    }
                }, error => {
                    this.$toasted.error(error.response.data.description)
                })
            }
        },
        selectedGroup: function (val) {
            if (this.init > 0) {
                this.init--
            } else {
                this.selectedGroup = val
                this.$emit('update:group', val)
                participationAPI.update(this.cID, {user_id: this.user.id, group: this.selectedGroup, role: this.selectedRole})
                    .catch(error => {
                        this.$toasted.error(error.response.data.description)
                    })
            }
        },
        group: function (newVal) {
            this.selectedGroup = newVal
        }
    },
    created () {
        this.selectedRole = this.user.role
        this.selectedGroup = this.group
    },
    components: {
        icon,
        profilePicture
    }
}
</script>
