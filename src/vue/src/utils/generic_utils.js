/* Expects a start date of the format "YY-mm-dd" */
export default {
    yearOffset (startDate) {
        let split = startDate.split('-')

        if ((split[1] === '2' || split[1] === '02') && split[2] === '29') {
            split[2] = '01'
            split[1] = '03'
        }

        let yearOff = parseInt(split[0]) + 1

        split[0] = String(yearOff)
        return split.join('-')
    },

    parseArrayBufferResponseErrorData (error) {
        let enc = new TextDecoder('utf-8')

        return JSON.parse(enc.decode(error.response.data))
    },

    /* Converts an arraybuffer response to a humanreadable description and displays it as an error. */
    displayArrayBufferRequestError (toasted, error) {
        toasted.error(this.parseArrayBufferResponseErrorData(error).description)
    }
}
