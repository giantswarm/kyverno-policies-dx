{{/* vim: set filetype=mustache: */}}

{{/*
Common labels
*/}}
{{- define "labels.common" -}}
app.kubernetes.io/managed-by: {{ .Release.Service | quote }}
application.giantswarm.io/team: {{ index .Chart.Annotations "io.giantswarm.application.team" | quote }}
helm.sh/chart: {{ include "chart" . | quote }}
giantswarm.io/service-type: managed
{{- end -}}
