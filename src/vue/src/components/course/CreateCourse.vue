<template>
    <b-card class="no-hover">
        <b-form @submit.prevent="onSubmit" @reset.prevent="onReset" :v-model="form.lti_id">
            <h2 class="field-heading required">Course name</h2>
            <b-input class="multi-form theme-input" v-model="form.name" placeholder="Course name"/>
            <h2 class="field-heading required">Course abbreviation</h2>
            <b-input class="multi-form theme-input" v-model="form.abbreviation" maxlength="10" placeholder="Course abbreviation (max 10 characters)"/>
            <b-row>
                <b-col cols="6">
                    <h2 class="field-heading required">From</h2>
                    <flat-pickr class="multi-form multi-date-input theme-input full-width" v-model="form.startdate"/>
                </b-col>
                <b-col cols="6">
                    <h2 class="field-heading required">To</h2>
                    <flat-pickr class="multi-form multi-date-input theme-input full-width" v-model="form.enddate"/>
                </b-col>
            </b-row>
            <b-button class="float-left change-button" type="reset">
                <icon name="undo"/>
                Reset
            </b-button>
            <b-button class="float-right add-button" type="submit">
                <icon name="plus-square"/>
                Create
            </b-button>
        </b-form>
    </b-card>
</template>

<script>
import courseAPI from '@/api/course'
import icon from 'vue-awesome/components/Icon'
import genericUtils from '@/utils/generic_utils.js'
import commonAPI from '@/api/common'

export default {
    name: 'CreateCourse',
    props: ['lti'],
    data () {
        return {
            form: {
                name: '',
                abbreviation: '',
                startdate: '',
                enddate: '',
                lti_id: ''
            }
        }
    },
    methods: {
        formFilled () {
            return this.form.name && this.form.abbreviation && this.form.startdate && this.form.enddate
        },
        onSubmit () {
            if (this.formFilled()) {
                courseAPI.create(this.form)
                    .then(course => {
                        if (!this.lti) { // If we are here via LTI a full store update will take place anyway.
                            commonAPI.getPermissions(course.id).then(coursePermissions => {
                                this.$store.commit('user/UPDATE_PERMISSIONS', { permissions: coursePermissions, key: 'course' + course.id })
                            })
                        }
                        this.$emit('handleAction', course.id)
                    })
                    .catch(error => { this.$toasted.error(error.response.data.description) })
            } else {
                this.$toasted.error('One or more required fields are empty.')
            }
        },
        onReset (evt) {
            this.form.name = ''
            this.form.abbreviation = ''
            this.form.startdate = ''
            this.form.enddate = ''
        }
    },
    mounted () {
        if (this.lti !== undefined) {
            this.form.name = this.lti.ltiCourseName
            this.form.abbreviation = this.lti.ltiCourseAbbr
            this.form.lti_id = this.lti.ltiCourseID
            this.form.startdate = this.lti.ltiCourseStart.split(' ')[0]
            this.form.enddate = genericUtils.yearOffset(this.form.startdate)
        }
    },
    components: {
        icon
    }
}
</script>
