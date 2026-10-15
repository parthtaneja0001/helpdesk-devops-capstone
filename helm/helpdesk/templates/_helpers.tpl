{{- define "helpdesk.labels" -}}
app.kubernetes.io/name: helpdesk
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/* usage: include "helpdesk.selector" (dict "ctx" $ "component" "backend") */}}
{{- define "helpdesk.selector" -}}
app.kubernetes.io/name: helpdesk
app.kubernetes.io/instance: {{ .ctx.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}
