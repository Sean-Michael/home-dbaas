{{- define "postgres.labels" -}}
        app: {{ .Release.Name }}-postgres
        chart: {{ .Chart.Name }}-{{ .Chart.Version }}
        release: {{ .Release.Name }}
{{- end -}}

{{- define "postgres.selectorLabels" -}}
        app: {{ .Release.Name }}-postgres
        release: {{ .Release.Name }}
{{- end -}}