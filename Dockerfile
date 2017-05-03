FROM alpine:3.5

MAINTAINER Miguel Gagliardo <migag21@yahoo.com.ar>

WORKDIR /terraform_validate

RUN apk update && apk upgrade && \
    apk --no-cache add python ca-certificates && \
    update-ca-certificates && \
    apk --no-cache add py2-pip && \
    pip install --no-cache-dir --upgrade pip terraform_validate

CMD [ "python", "tests.py" ]

