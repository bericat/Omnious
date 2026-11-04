Shader "Ominous/Video Lit"
{
    Properties
    {
        _BaseMap ("Textura", 2D) = "white" {}
        _BaseColor ("Color", Color) = (1,1,1,1)
        _EmissionColor ("Emisión", Color) = (0,0,0,1)
        _AmbientBoost ("Ambiente extra (exterior)", Float) = 1
        _Exterior ("Niebla de exterior", Float) = 0
        _RoomAO ("Oscurecer junto a suelo y techo", Float) = 0
        _Sheen ("Brillo discreto", Range(0, 1)) = 0
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" "Queue"="Geometry" }
        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4 _BaseColor;
            half4 _EmissionColor;
            float _AmbientBoost;
            float _Exterior;
            float _RoomAO;
            float _Sheen;
        CBUFFER_END
        ENDHLSL

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForward" }
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _ADDITIONAL_LIGHTS _ADDITIONAL_LIGHTS_VERTEX
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
            half4 _Video_Ambient;
            half4 _Video_FogColor;
            half4 _Video_ExteriorFogColor;
            float4 _Video_Fog;         // x-y: niebla interior, inicio y fin
            float4 _Video_ExteriorFog; // x-y: niebla exterior, inicio y fin

            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; float2 uv : TEXCOORD0; };
            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                float3 normalWS : TEXCOORD2;
            };

            Varyings Vert(Attributes i)
            {
                Varyings o;
                o.positionWS = TransformObjectToWorld(i.positionOS.xyz);
                o.normalWS = TransformObjectToWorldNormal(i.normalOS);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.uv = TRANSFORM_TEX(i.uv, _BaseMap);
                return o;
            }

            half3 Sheen(float3 n, float3 v, float3 l, half3 color)
            {
                float3 h = normalize(l + v);
                return color * pow(saturate(dot(n, h)), 28.0) * _Sheen;
            }

            half4 Frag(Varyings i) : SV_Target
            {
                half3 tex = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv).rgb;
                half3 albedo = tex * _BaseColor.rgb;
                float3 n = normalize(i.normalWS);
                float3 v = normalize(GetCameraPositionWS() - i.positionWS);
                // Ambiente desigual: entra algo más de luz desde arriba que desde abajo.
                half3 light = _Video_Ambient.rgb * _AmbientBoost * (0.72 + 0.28 * n.y);
                half3 spec = 0;

                #if defined(_ADDITIONAL_LIGHTS)
                InputData inputData = (InputData)0;
                inputData.positionWS = i.positionWS;
                inputData.normalWS = n;
                inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(i.positionCS);
                uint pixelLightCount = GetAdditionalLightsCount();
                LIGHT_LOOP_BEGIN(pixelLightCount)
                    Light l = GetAdditionalLight(lightIndex, i.positionWS, half4(1,1,1,1));
                    half3 c = l.color * l.distanceAttenuation * l.shadowAttenuation;
                    light += c * saturate(dot(n, l.direction));
                    spec += Sheen(n, v, l.direction, c);
                LIGHT_LOOP_END
                #endif

                if (_RoomAO > 0.5)
                {
                    float edge = saturate(min(i.positionWS.y / 0.5, (2.6 - i.positionWS.y) / 0.5));
                    light *= lerp(0.55, 1.0, edge);
                }

                half3 color = albedo * light + spec + _EmissionColor.rgb * tex;
                float d = distance(i.positionWS, GetCameraPositionWS());
                if (_Exterior > 0.5)
                {
                    float fog = saturate((d - _Video_ExteriorFog.x) / max(0.001, _Video_ExteriorFog.y - _Video_ExteriorFog.x));
                    color = lerp(color, _Video_ExteriorFogColor.rgb, fog);
                }
                else
                {
                    float fog = saturate((d - _Video_Fog.x) / max(0.001, _Video_Fog.y - _Video_Fog.x));
                    color = lerp(color, _Video_FogColor.rgb, fog);
                }
                return half4(color, 1);
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode"="ShadowCaster" }
            ZWrite On
            ZTest LEqual
            ColorMask 0
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"
            float3 _LightDirection;
            float3 _LightPosition;
            float4 Vert(float4 p : POSITION, float3 normal : NORMAL) : SV_POSITION
            {
                float3 ws = TransformObjectToWorld(p.xyz);
                float3 ns = TransformObjectToWorldNormal(normal);
                #if _CASTING_PUNCTUAL_LIGHT_SHADOW
                float3 dir = normalize(_LightPosition - ws);
                #else
                float3 dir = _LightDirection;
                #endif
                float4 c = TransformWorldToHClip(ApplyShadowBias(ws, ns, dir));
                #if UNITY_REVERSED_Z
                c.z = min(c.z, UNITY_NEAR_CLIP_VALUE);
                #else
                c.z = max(c.z, UNITY_NEAR_CLIP_VALUE);
                #endif
                return c;
            }
            half Frag() : SV_Target { return 0; }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode"="DepthOnly" }
            ZWrite On
            ColorMask R
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            float4 Vert(float4 p : POSITION) : SV_POSITION { return TransformObjectToHClip(p.xyz); }
            half Frag() : SV_Target { return 0; }
            ENDHLSL
        }
    }
}
