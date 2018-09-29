<template>
    <b-link tag="b-button" :to="{ name: 'Journal',
                                  params: {
                                      cID: cID,
                                      aID: aID,
                                      jID: jID
                                  }, query: query
                                }">

        <student-card
            :student="jStudent"
            :stats="jStats">
        </student-card>
    </b-link>
</template>

<script>
import studentCard from '@/components/assignment/StudentCard.vue'

export default {
    name: 'StudentLinkCard',
    props: {
        cID: {
            required: true
        },
        aID: {
            required: true
        },
        jID: {
            required: true
        },
        query: {
            required: true
        },
        jStudent: {
            required: true
        },
        jStats: {
            required: true
        }
    },
    components: {
        'student-card': studentCard
    }
}
</script>
