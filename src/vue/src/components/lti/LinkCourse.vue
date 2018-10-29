<template>
    <b-card class="no-hover">
        <div v-for="c in courses" :key="c.id">
            <div v-if="c.lti_couples">
                <main-card
                    class="orange-border"
                    @click.native="linkCourse(c)"
                    :line1="c.name"
                    :line2="c.startdate.substring(0, 4) + '-' + c.enddate.substring(0, 4)"/>
            </div>
            <div v-else>
                <main-card
                    class="green-border"
                    @click.native="linkCourse(c)"
                    :line1="c.name"
                    :line2="c.startdate.substring(0, 4) + '-' + c.enddate.substring(0, 4)"/>
            </div>
        </div>
    </b-card>
</template>

<script>
import mainCard from '@/components/assets/MainCard.vue'
import courseAPI from '@/api/course'

export default {
    name: 'LinkCourse',
    props: ['lti', 'courses'],
    components: {
        'main-card': mainCard
    },
    methods: {
        linkCourse (c) {
            if (!c.lti_couples || confirm('This course is already linked to ' + c.lti_couples + ' other course(s) from the learning-environment, are you sure you also want to link it?')) {
                courseAPI.update(c.id, {lti_id: this.lti.ltiCourseID})
                    .then(course => { this.$emit('handleAction', course.id) })
            }
        }
    }
}
</script>
